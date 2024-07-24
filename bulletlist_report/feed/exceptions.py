class NotImplementedException(Exception):
    """Exception raised for not implemented features."""
    def __init__(self, feature_name):
        self.feature_name = feature_name
        super().__init__(f"The feature '{feature_name}' has not been implemented yet.")