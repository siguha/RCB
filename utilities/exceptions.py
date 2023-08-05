class Exceptions:
    class UserNotFound(Exception):
        """Raised when a given DiscordID is not found in the database."""
        pass