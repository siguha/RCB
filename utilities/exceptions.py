class Exceptions:
    class UserNotFound(Exception):
        """Raised when a given DiscordID is not found in the database."""
        pass

    class LogNotFound(Exception):
        """Raised when an AAR log is not found in the AAR sheet."""
        pass
    
    class LOANotFound(Exception):
        """Raised when an LOA doesn't exist in LOA sheet."""
        pass
    
    class LOAExisting(Exception):
        """Raised when a user has an active LOA."""
        pass