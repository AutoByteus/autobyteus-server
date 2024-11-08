class HackathonSearchResult:
    """
    A data structure for hackathon search results containing a list of file paths.
    """
    
    def __init__(self, paths: list):
        """
        Initializes the HackathonSearchResult with a list of file paths.
        
        Args:
            paths (list): A list of file path strings.
        """
        self.paths = paths
    
    def to_json(self) -> str:
        """
        Converts the search result to a JSON string.
        
        Returns:
            str: JSON representation of the search result.
        """
        import json
        return json.dumps({"paths": self.paths})