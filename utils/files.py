import zipfile
import tarfile
import pathlib


def unzip(fp):
    fp = pathlib.Path(fp)

    if PLATFORM == 'Linux':
        import tarfile
        with tarfile.open(fp) as f:
            f.extractall(fp.parent)
    else:
        with zipfile.ZipFile(fp, 'r') as f:
            f.extractall(fp.parent)


def zipdir(path, outpath):
    ziph = zipfile.ZipFile(outpath, 'w', zipfile.ZIP_DEFLATED)
    try:
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
    except:
        raise Exception("zip error")
    finally:
        ziph.close()



def rm(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=True)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def tempfile(name="temp.md"):
    with open(name, "w") as f:
        f.write("\n")
    return str(pathlib.Path(name).absolute())




def exc_path(program):
    """Test if executable exists
    """
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
