# Minimal code for querying an embedding model

This repo contains extremely minimal code for querying an arbitrary Hugging Face Sentence Transformer embedding model, running on
an infinity server on a Runpod instance.

The idea is to show a fast, easy, quite cheap way to set up an embedding model running on a dedicated GPU. One can then send API requests to the server with text to embed, and receive embeddings in response.

I have no affiliation with HF infinity server or Runpod.

## How to setup an infinity server on a Runpod instance

### Useful commands:

First off, here are some useful commands for interfacing with a remote server:

- Connect to remote server via SSH over exposed TCP (Supports SCP & SFTP):

```
ssh root@{IP_ADDRESS} -p {PORT} -i ~/.ssh/id_ed25519
```

This assumes your SSH keys are stored in `~/.ssh/id_ed25519`. You can also use an RSA-formatted SSH key
if desired. If unfamiliar with SSH keys
see one of the many available guides online, e.g. https://docs.oracle.com/en/cloud/cloud-at-customer/occ-get-started/generate-ssh-key-pair.html

- Transfer files to remote server:

```
scp -r -P {PORT} -i ~/.ssh/id_ed25519 . root@{IP_ADDRESS}:workspace
```

### Setting up Runpod

For this tutorial to work, you'll need a Runpod account. Here is the runpod website: https://www.runpod.io/ .

Just follow the steps for creating a new instance: load some credits, add your SSH keys so you
can SSH into the machine, and start up an instance. I tend to go for the cheapest GPU option,
the RTX A4000.

The only annoying thing I found about Runpod is that they don't seem to have any available text editors
that one can interact with on the machine. I.e., once you upload a file, you can't make changes to it locally
on the server via opening a text editor via the shell. There may be a way to do it, but I didn't find
one (e.g. `vim`, `nano`, etc. don't work). It may be a security feature they have.

Later on I have a section: `Using other cloud compute providers`

### Starting up an infinity server on runpod instance for testing open source models:

To get started (once you have an account, credits and have added your SSH key to Runpod),
first, start up an Runpod instance. The following is up to date as of 29/06/2024, but the UI of Runpod may have changed since then.

Go to pods, and click Deploy.
![alt text](<README_figs/Image 29-06-2024 at 14.05.jpg>)

I normally select the cheapest GPU option of RTX A4000, with the default settings. Make sure
the SSH terminal access is option is selected.
![alt text](<README_figs/Image 29-06-2024 at 14.06.jpg>)

Then just click `Deploy on-demand` at the bottom.

As the instance is getting ready, go to your pods and select your pod and open up the full view. Go to the `More Actions` in the bottom left:
![alt text](<README_figs/Image 29-06-2024 at 14.10.jpg>)

From there, edit the pod:
![alt text](<README_figs/Screenshot 2024-06-11 at 13.23.50.png>)

Add port 7997 to the exposed ports.
![alt text](<README_figs/Screenshot 2024-06-11 at 13.23.35.png>)

Once the pod is ready, SSH into the runpod instance. Easiest to use the
basic SSH terminal, with the ID. Note the ID as `RUNDPOD_ID`. In this case, `RUNDPOD_ID='fhpz055jlhlkav-64410a2b'`.

![alt text](<README_figs/Screenshot 2024-06-11 at 13.30.29.png>)

Then, install the infinity server onto the runpod instance (via the SSH connection).

```
pip install infinity-emb[all]
```

Start up the desired model. In this case, we use the `BAAI/bge-m3` embedding model:

```
infinity_emb v2 --model-id BAAI/bge-m3
```

From a new local terminal, you can now send requests to the runpod infinity instance to get embeddings from infinity server:

```
curl -v -X 'POST'
  'https://{RUNPOD_ID}-{INTERNAL_INF_PORT}.proxy.runpod.net/embeddings' -H 'Content-Type: application/json' -d '{
  "input": ["query"],
  "model": "BAAI/bge-m3",
  "user": "string"
}'
```

where `RUNPOD_ID` is the runpod ID, and `INTERNAL_INF_PORT` is the internal exposed port on the
runpod server for the infinity server (which is not the same as the Runpod `PORT`). In our
example, `INTENRAL_INF_PORT = 7997`.
You can also make API requests to the server from inside a Python script.

```python
import requests
server_address = f"https://{RUNPOD_ID}-{RUNPOD_INTERNAL_INF_PORT}.proxy.runpod.net/embeddings"
data = {"input": input_texts, "model": "BAAI/bge-m3"]}
response = requests.post(server_address, json=data)
```

As one makes requests to the server, one should see it logging the requests in the runpod terminal (if
one is still SSH'd into the runpod instance).

![alt text](<README_figs/Screenshot 2024-06-11 at 13.41.32.png>)

**NOTE:** it's important to kill the runpod instance after one is done with it
otherwise it'll just eat up your credits in thr background.

### Using other cloud compute providers

This tutorial uses Runpod because I found it to be quick and easy to
mess around with and relatively cheap, but the code will work for your preferred cloud compute provider,
just swap out the `server_address` in the code. Follow the same steps as above, i.e. start an instance, expose
the desired port number, install the infinity server and run your desired model. Note down the server
address and add it to your code.

Once done with your compute, power down the instance to avoid getting hit with
a big cloup compute bill. Expect that after powering down the instance, your code will no longer
work and next time you spin up a new instance you will need to follow all of the same steps over
again, including updating the server adress.

### Quirk of infinity server

One should make sure that the model one is referencing in one's API call is the same as the one
that is running on the server.

In practice, infinity seems to swap out the models as needed on the fly depending on thje model name in our API call, but in my paranoia
(and I've been to lazy to dive into the infinity server code to see how it happens) it still
makes me a bit nervous, so I'd advise against relying on the infinity server to swap them out. I would recommend making sure the model you set up on the infinity server matches that in your API call.
