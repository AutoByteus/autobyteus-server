#!/bin/bash

# Function to print colored status messages
print_status() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color
    echo -e "${GREEN}[Setup] $1${NC}"
}

# Function to print error messages
print_error() {
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    echo -e "${RED}[Error] $1${NC}"
}

# Function to print debug messages
print_debug() {
    YELLOW='\033[1;33m'
    NC='\033[0m' # No Color
    echo -e "${YELLOW}[Debug] $1${NC}"
}

# Check if script is run with sudo
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script with sudo"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    print_error "jq is required but not installed. Please install it first."
    print_status "You can install it using: sudo apt-get install jq"
    exit 1
fi

# Get the absolute path to the repository root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Get the actual user who ran the script with sudo
ACTUAL_USER="${SUDO_USER:-$USER}"
USER_ID=$(id -u "$ACTUAL_USER")
GROUP_ID=$(id -g "$ACTUAL_USER")

# Setup hosts file for local development
print_status "Setting up hosts file for local development..."
if grep -q "mongo1" /etc/hosts; then
    print_debug "Hosts entries already exist"
else
    print_debug "Adding mongo1, mongo2, mongo3 to /etc/hosts"
    echo "127.0.0.1 mongo1 mongo2 mongo3" >> /etc/hosts
fi

# Function to check container status
check_container_status() {
    local container_name=$1
    print_debug "Checking status of container: $container_name"
    
    if ! docker ps | grep -q "$container_name"; then
        print_debug "Container $container_name not running"
        print_debug "Docker PS output:"
        docker ps
        print_debug "Docker PS -a output:"
        docker ps -a
        print_debug "Docker logs for $container_name:"
        docker logs "$container_name" 2>&1 || true
        return 1
    fi
    
    return 0
}

# Function to check MongoDB readiness
check_mongodb_ready() {
    local container_name=$1
    print_debug "Checking MongoDB readiness for container: $container_name"
    
    # Try to connect and check status
    if docker exec "$container_name" mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        print_debug "MongoDB is responding in container $container_name"
        return 0
    else
        print_debug "MongoDB not ready in container $container_name"
        print_debug "Container logs:"
        docker logs "$container_name" --tail 50
        return 1
    fi
}

# Display MongoDB version being used
print_status "Checking MongoDB version..."
MONGO_VERSION=$(docker run --rm mongo:latest mongod --version | grep "db version" | cut -d " " -f 3)
print_status "Using MongoDB version: $MONGO_VERSION"

# Warning about data cleanup
print_status "WARNING: This script will remove existing MongoDB data directories for a clean setup"
read -p "Do you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

DATA_DIR="$REPO_ROOT/deployment/docker/mongodb/data"

# Remove existing data directories
print_status "Cleaning up existing MongoDB data..."
rm -rf "$DATA_DIR"

# Create MongoDB data directories
print_status "Creating MongoDB data directories..."
mkdir -p "$DATA_DIR/mongo1"
mkdir -p "$DATA_DIR/mongo2"
mkdir -p "$DATA_DIR/mongo3"

# Set permissions and ownership
print_status "Setting directory permissions..."
chown -R ${USER_ID}:${GROUP_ID} "$DATA_DIR"
chmod -R 700 "$DATA_DIR"

# Start MongoDB containers
print_status "Starting MongoDB containers..."
cd "$REPO_ROOT/deployment/docker" || exit
docker-compose down -v
print_debug "Removed existing containers and networks"

docker-compose up -d
print_debug "Started new containers"

# Get container names
CONTAINER1="docker_mongo1_1"
CONTAINER2="docker_mongo2_1"
CONTAINER3="docker_mongo3_1"

# Function to wait for MongoDB containers
wait_for_mongodb() {
    print_status "Waiting for MongoDB containers to be ready..."
    local max_attempts=60  # 60 seconds timeout
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_debug "Attempt $attempt of $max_attempts"
        
        # Check if containers are running
        for container in "$CONTAINER1" "$CONTAINER2" "$CONTAINER3"; do
            if ! check_container_status "$container"; then
                print_debug "Container $container not ready yet"
                sleep 2
                attempt=$((attempt + 1))
                continue 2
            fi
        done
        
        # Check if MongoDB is responding
        for container in "$CONTAINER1" "$CONTAINER2" "$CONTAINER3"; do
            if ! check_mongodb_ready "$container"; then
                print_debug "MongoDB in $container not ready yet"
                sleep 2
                attempt=$((attempt + 1))
                continue 2
            fi
        done
        
        print_status "All containers are ready!"
        return 0
    done
    
    print_error "Timeout waiting for MongoDB to start"
    return 1
}

# Wait for MongoDB to be ready
if ! wait_for_mongodb; then
    print_error "Failed to start MongoDB cluster"
    print_debug "Final container states:"
    docker ps -a
    print_debug "Network status:"
    docker network ls
    print_debug "Docker compose logs:"
    docker-compose logs
    exit 1
fi

print_status "Initializing replica set..."
if ! docker exec $CONTAINER1 mongosh --eval '
rs.initiate({
 _id: "rs0",
 members: [
   {_id: 0, host: "mongo1:27017", priority: 2},
   {_id: 1, host: "mongo2:27017", priority: 1},
   {_id: 2, host: "mongo3:27017", priority: 1}
 ]
})'; then
    print_error "Failed to initialize replica set"
    print_debug "Container logs:"
    docker logs $CONTAINER1
    exit 1
fi

# Wait for replica set to initialize and elect primary
print_status "Waiting for replica set to initialize and elect primary..."
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    print_debug "Checking replica set status (attempt $attempt of $max_attempts)..."
    
    # Get replica set status
    rs_status=$(docker exec $CONTAINER1 mongosh --quiet --eval '
    var status = rs.status();
    var primary = status.members.filter(m => m.state === 1)[0];
    var secondary = status.members.filter(m => m.state === 2);
    printjson({
        ok: status.ok,
        primary: primary ? primary.name : null,
        secondaries: secondary.length,
        members: status.members.map(m => ({name: m.name, state: m.stateStr}))
    });
    ')
    
    print_debug "Current replica set status: $rs_status"
    
    # Use jq to parse the JSON and check status
    if echo "$rs_status" | jq -e '.primary != null and .secondaries >= 1' >/dev/null 2>&1; then
        print_status "Replica set is fully initialized!"
        
        # Extract information using jq
        primary_node=$(echo "$rs_status" | jq -r '.primary')
        secondary_count=$(echo "$rs_status" | jq -r '.secondaries')
        
        print_status "Primary node: $primary_node"
        print_status "Number of secondaries: $secondary_count"
        print_status "Connection string: mongodb://localhost:27017/?replicaSet=rs0"
        
        # Show final configuration
        print_status "Final replica set configuration:"
        echo "$rs_status" | jq '.members'
        
        exit 0
    fi
    
    print_debug "Waiting for primary election... (5 seconds)"
    sleep 5
    attempt=$((attempt + 1))
done

print_error "Failed to verify replica set status after $max_attempts attempts"
print_debug "Final replica set status:"
docker exec $CONTAINER1 mongosh --eval 'rs.status()'
exit 1