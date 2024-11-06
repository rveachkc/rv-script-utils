# rv-script-utils

Script utilities to add in structured logging and support for healthchecks.io.
See example of use in hello.py and in the example below.

```python
from typing import Self

from rv_script_lib import ScriptBase


class HelloWorld(ScriptBase):

    PARSER_ARGPARSE_KWARGS = {
        "description": "Hello World",
    }

    def extraArgs(self: Self):

        self.parser.add_argument(
            "-m",
            "--message",
            type=str,
            dest="message",
            default="you forgot to add a message with -m/--message",
            help="What do you want to say?",
        )

    def runJob(self: Self):

        self.log.info("Hello from rv-script-utils!")

        try:
            raise RuntimeError("This is just a test")
        except Exception as e:
            self.log.exception(e)

        self.log.warning("Warning, just for fun")

        self.log.info(self.args.message)


if __name__ == "__main__":

    myscript = HelloWorld()
    myscript.run()
```
