# Notebooks

For this project, we sometimes use Jupyter (`.ipynb`) notebooks to explore data and experiment with code. The notebooks are stored in the `notebooks` directory.

Some points to note about the notebooks:

* The notebooks are **not** part of the main application and are not intended to be run as part of any of the scheduled pipelines of the project.

* The notebooks are **not** guaranteed to be up-to-date or to work with the latest version of the code. They are provided as a convenience for developers for experimentation and exploration.

* The `.py` representation of notebooks however are version controlled. More information about versioning can be found in the [Versioning](#versioning) section.

## Versioning

For this project we are using Azure Repos as the VCS platform and at the time of writing this doc Azure Repos does not support a clean way of versioning of `.ipynb` files and hence in PRs git treats them as huge JSON blobs which are not at all developer friendly
 especially when there are merge conflicts.

To avoid this, we have decided to use a 3rd party `pip` package called [`jupytext`](https://jupytext.readthedocs.io/en/latest), which helps us export and pair all the `.ipynb` files with `.py` files, in conjunction with [VSCode Tasks](https://code.visualstudio.com/docs/editor/tasks#_custom-tasks).
 This way we can version control the `.py` files and the `.ipynb` files can be ignored and generated on the fly.

## Workflow 

### Adding new notebooks

Do the following:

1. Create a new `.ipynb` file and write your code in it.

2. After you are done making changes just save them - this would automatically create a new `.py` file with the same name as your notebook in the same location (this is the [_paired_](https://jupytext.readthedocs.io/en/latest/paired-notebooks.html#)
 Python script)

3. Add it to the index of the git repo (as initially it would be untracked) and then commit it.

### Updating existing notebooks 

Do the following:

1. Run the following to create a new `.ipynb` file from the `.py` file you would like to work on:

    ```shell

    jupytext --to notebook <path to your notebook>.py

    ```

2. This creates a new `.ipynb` file with the same name as your `.py` file in the same location. You can now open this `.ipynb` file and make changes.

3. After you are done making changes to the `.ipynb` file, just save them - this would automatically update the
_paired_ `.py` file (one that has the same name).

4. Commit the new changes made to the paired `.py` file.


Note all `ipynb` files are ignored in the `.gitignore` file and hence you should not commit them. At any point in time we should always have
**only** `.py` files under the `notebooks` folder in the remote repo.


Note sometimes the supporting VSCode Task may not start itself in the background upon launching the IDE. You may need to start it manually once by running the following in the Command Palette:

```

>Tasks: Run Task 

```

and select the `watch ipynb` task from the the dropdown list.