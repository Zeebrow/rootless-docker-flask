# Rootless Docker with Flask

"Rootless" immediately sounds great. But I don't know how it works.

This is a simple dive into it.

### requierments

This is done after setting up [rootless-docker](https://docs.docker.com/engine/security/rootless/) on my Ubuntu host.

I already head the rooty tooty Docker installed, along with a Kubernetes cluster running on it. So yeah, there's some ugly hiding.

## usage

```
git clone https://github.com/Zeebrow/rootless-docker-flask
cd rootless-docker-flask
docker build -t local/rootless-flask .
docker run -d --rm --name rootless-flask -p5000:5000 local/rootless-flask
curl localhost:5000/sysinfo # gets some info from inside the container
```
This will show `"user-getpass": "appuser"` as defined in the Dockerfile.


## Notes

You can pass `-u root` to `docker run` for the container to behave like a
more-familiar root container.

```
docker rm -f local/rootless-flask
docker run -d --rm --name rootless-flask -p5000:5000 -u root local/rootless-flask
```

Either the term "rootless" is misleading, or I'm doing something wrong here.

## Thoughts

### A multi-stage build would be ideal to bring the image size down (124MB = yikes)

### It would be neet to be able to configure the response as the container is running
Say for example you build the container, with your Python app importing `json`,`os`,`sys`, etc. 

Add a custom Flask route, say, `/myconfig`. It returns `jsonify(json.load(fd))`, where `fd` is a your `open()` config file on the docker host. This file would look something like:

```
{
  "whatever you want": sys.path,
  "another thing you want": os.getenv('foo')
}
```

Under the hood, Python would use `exec()` to run the code\*. Quick n dirty:

```
@app.route('/myconfig')
def myconfig(maybe_query_string_here=None):
  with open('config_filepath.json', 'r') as cfg:
    j = json.load(cfg)
  for your_key, your_value in j.items():
    rtn[your_key] = exec(your_value)
  return Jsonify(rtn)
```

then you can `curl localhost:5000/myconfig` to see how various Python modules behave in a container.

Theoretically, you've got the Python interpreter at your disposal here, and you can't really fuck anything up because you're in a container.

\*Obviously, Terms and Conditions apply. See store for details

## More info

[Great in-depth guide to rootlessness (That I need to finish reading)](https://rootlesscontaine.rs/)

[USER Dockerfile directive](https://docs.docker.com/engine/reference/builder/#user)

[rootless-docker](https://docs.docker.com/engine/security/rootless/)
