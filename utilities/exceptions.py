class Exceptions:
    class UserNotFound(Exception):
        """Raised when a given DiscordID is not found in the database."""
        pass

    class LogNotFound(Exception):
        """Raised when an AAR log is not found in the AAR sheet."""
        pass