import click
import os
import shutil


@click.group()
def resetmigrations():
    """
    Commands to clear all django migrations files and pycache.
    """
    pass


@click.command(name='clean')
@click.option('--path', '-p',
              help="""
              Specific top 'tree' path. Defaults to None
              """,
              required=False)
def clean(path: str = None):
    """
    Cleans migrations and pycaches.

    Args:
        path (str, optional): Specific top 'tree' path. Defaults to None.
    """

    if path is None:
        path = os.path.dirname(os.path.abspath(__file__))
        print("path is", path)

    try:
        click.echo("Cleaning migrations and pycaches")
        clean_dir(path)
    except Exception as e:
        click.echo(f"Failed: {e}")


def clean_dir(path):
    """Cleans migrations and pycaches.

    Args:
        path (str): Specific top 'tree' path.
    """
    click.echo(
        f"Cleaning migrations and pycaches in {path}")

    # Change to the directory provided
    os.chdir(path)

    # Store the current directory
    cwd = os.getcwd()

    # If it is not a directory, inmediately return
    if not os.path.isdir(path):
        return

    # Get the name
    cwd_name = os.path.basename(cwd)

    if cwd_name in ["virtualenv", "venv", "env"]:
        print("This is a virtualenv, skipping...")
        return

    # If the directory is empty, return inmediately
    if os.listdir() == 0:
        print("This is an empty directory, skipping...")
        return

    for element in os.listdir():
        # If the element is a directory, call the function recursively
        path_to_element = f'{cwd}\\{element}'

        if element == "__pycache__":
            shutil.rmtree(path_to_element)
            continue

        if os.path.isdir(path_to_element):
            clean_dir(path_to_element)
        elif cwd_name == 'migrations':
            if element == "__init__.py":
                continue
            else:
                os.remove(path_to_element)


resetmigrations.add_command(clean)


def main():
    # clean_dir(os.path.dirname(os.path.abspath(__file__)))
    resetmigrations()


if __name__ == '__main__':
    main()
