from autobyteus_server.search.hackathon_search_result import HackathonSearchResult

class HackathonSearchService:
    """
    A fake search service for hackathon purposes that returns fixed file paths based on the query.
    """
    
    def search(self, query: str) -> HackathonSearchResult:
        """
        Returns a fixed list of file paths regardless of the query.
        
        Args:
            query (str): The search query.
        
        Returns:
            HackathonSearchResult: The search result containing fixed file paths.
        """
        fixed_paths = [
            "src/project/module1/file1.py",
            "src/project/module2/file2.py",
            "src/project/module3/file3.py"
        ]
        return HackathonSearchResult(paths=fixed_paths)