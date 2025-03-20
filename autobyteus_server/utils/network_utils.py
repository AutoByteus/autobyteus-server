import socket
import logging
import re
import netifaces

logger = logging.getLogger(__name__)

def is_private_ip(ip):
    """
    Check if an IP address matches private IP patterns.
    
    Args:
        ip (str): The IP address to check.
        
    Returns:
        bool: True if the IP is a private address, False otherwise.
    """
    # First validate that it's a properly formatted IP address
    try:
        # This will split the IP and validate each octet is 0-255
        octets = ip.split('.')
        if len(octets) != 4:
            return False
        for octet in octets:
            num = int(octet)
            if num < 0 or num > 255:
                return False
    except (ValueError, AttributeError):
        return False
        
    # Now check if it matches private IP ranges
    private_patterns = [
        r'^10\.\d+\.\d+\.\d+$',                # 10.0.0.0 - 10.255.255.255
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+$',  # 172.16.0.0 - 172.31.255.255
        r'^192\.168\.\d+\.\d+$'                # 192.168.0.0 - 192.168.255.255
    ]
    return any(re.match(pattern, ip) for pattern in private_patterns)

def get_local_ip():
    """
    Get the local private IP of the active interface.
    
    This function attempts different methods to find a suitable local IP:
    1. First tries the socket method by establishing a connection to a public DNS
    2. If that fails, uses netifaces to search through all available interfaces
    
    Returns:
        str: The detected local IP address, or None if no suitable IP is found.
    """
    # Try socket method first (usually gets the active interface IP)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        
        if is_private_ip(ip):
            logger.info(f"Found local IP using socket method: {ip}")
            return ip
    except Exception as e:
        logger.debug(f"Socket method failed to get local IP: {str(e)}")
    
    # Fallback to netifaces method
    try:
        for interface in netifaces.interfaces():
            if interface == 'lo':  # Skip loopback
                continue
                
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if is_private_ip(ip) and ip != '127.0.0.1':
                        logger.info(f"Found local IP using netifaces from interface {interface}: {ip}")
                        return ip
                        
        logger.warning("No suitable local IP address found")
        return None
    except Exception as e:
        logger.error(f"Error using netifaces to get local IP: {str(e)}")
        return None
