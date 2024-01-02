import environ

env = environ.Env()


class HostingEnvironment:
    @classmethod
    def is_local(_cls):
        return env.str("ENVIRONMENT", None) == "LOCAL"
