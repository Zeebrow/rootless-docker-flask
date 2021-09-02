# Rootless Docker with Flask

"Rootless" immediately sounds great. Safety! Ownership! In case you're just joining, far too many Docker pages lack clarity and/or depth outside of the immediate usecases you're there searching for. (How could they? It's only a cross-platform container runtime that needs to support workloads of the likes of Kubernetes, up until recently) I want more details than what the Docker docs provide, in this case.

So here I threw up a little Flask api app (read: "Hello World++") that provides some info on what's going on under the hood of a rootless-Docker install.

I did learn a few interesting details about the daemon, but also about what it might mean to migrate a containerized app that was written under the assumption that container's runtime has root access.

### background

Rootless-Docker is a more secure way to run the Docker daemon.

This is done after setting up [rootless-docker](https://docs.docker.com/engine/security/rootless/) on my Ubuntu host.

I already head the rooty tooty Docker installed, along with a Kubernetes cluster running. HAd I been hosting anything of value, well, let's just say I wouldn't have been able to rush this out to build on like I've done. 

I wrote this taking for granted that rootless-Docker is installed and configured per the docs. Test for yourself with `cat /run/user/$(id -u)/docker.pid`

## usage

```
`./rebuild [user to run as]`
```

or

```
git clone https://github.com/Zeebrow/rootless-docker-flask
cd rootless-docker-flask
docker build -t local/rootless-flask .
docker run -d --rm --name rootless-flask -p5000:5000 local/rootless-flask
curl localhost:5000/sysinfo # gets some info from inside the container
```
This will show `"user-getpass": "appuser"` as defined in the Dockerfile on success.


## Notes

### Setting users when standing up a container

`-u` only works if the user exists inside the container. If the Dockerfile didn't have the first `RUN` directive, things would seems to work swimmingly - but Python would call `os.getpass.getuser()` and shit the bed, with something like "No user found for uid 1001" (or whatever was set with `USER`).

You can always pass `-u root` to `docker run` for the container to behave like a more-familiar root container. Not sure yet how different a "rootless root" user in a container is. Me thinks a lot not gonna work, man.

```
docker rm -f local/rootless-flask
docker run -d --rm --name rootless-flask -p5000:5000 -u root local/rootless-flask
```

Either the term "rootless" is misleading, or I'm doing something wrong here.

### Read/write access to bind mounts is determined by Docker host's file permissions

Not to be confused with "the Docker host's file ownership".

This must be a result of how `newuidmap` and `newgidmap` programs work (they're dependencies for rootless Docker). The man pages for these are really short.

Basically, it seems that if you want to write to files on a bind mount from inside a container, the permissions need to be set appropriately on the host. Which kind of makes sense. I dunno if this is the same for rooty Docker (I need to spin up a VM and try this out... sometime).

This holds even if the container user exists on the Docker host, and has the same `$(id)` in and outside of the container.

Yup, still true if you passed `-u root` with `docker run`. Only difference is you can frolic about in the container more freely. So if you're doing containers right, this makes no difference.

So far, so neat.

## Thoughts

### 124MB image size = yikes 
A multi-stage build could bring the image size down. I wonder how big a footprint the Golang equivalent would be - that'd be a fun Saturday! 

### It would be neet to be able to configure the response as the container is running
Totally unrelated to rootless docker. I wanted to think through a potential design pattern that is close to similar api projects I've written in the past.

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

Theoretically, you've got the Python interpreter at your disposal here, along with whatever packages you installed. And you can't really f anything up for anyone but yourself, because you're in a rootless container.

\*Obviously, Terms and Conditions apply. See store for details

## More info

[Great in-depth guide to rootlessness (That I need to finish reading)](https://rootlesscontaine.rs/)

[USER Dockerfile directive](https://docs.docker.com/engine/reference/builder/#user)

[rootless-docker](https://docs.docker.com/engine/security/rootless/)
