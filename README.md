# Do more in Paperless NGX using LLMs

This project is based on [**ngx-renamer**](https://github.com/chriskoch/ngx-renamer) by Christian Koch (chriskoch). I really enjoyed their work, but I had a real problem with sending my medical and tax documents, for instance, to OpenAI, and would much prefer to either send it to my own instance in the cloud or to a local instance of Ollama. 

I made updates to ngx-renamer to allow setting of preferred model, OpenAI or Ollama. Currently no support for other API integrations, but may add in the guture.

As I did, I realized there are other opportunities, so I am calling this **ngx-aitools** because I am going to try to add the following soon:
- Refactor code so that repetitive functions are pulled out in utils, which will help in future
- Ability to optionally use OpenAI as a backup if Ollama is unreachable
- Ability to have AI add tags based on content
- Ability to have AI assign Document Type based on content
- Ability to have AI add summary of doc in notes section
- (Maybe, skeptical this will work) Ability to have AI identify Correspondant from the content OR create a new one if it doesn't exist.

For now though, this is just a fork of ngx-renamer. I have mostly done the following:
- Add the ability to use Ollama
- Add the ability to set Ollama or OpenAI as the default LLM
- Added a test for testing based on an existing document
- Some fixes to instructions on how to set the URL
- Added place holder .env file
- Updated the query to get better results

# Renaming titles in Paperless NGX using Ollama or OpenAI

This is a Paperless NGX post consumption script. For more information on post consumption, see : https://docs.paperless-ngx.com/advanced_usage/#consume-hooks.
You either need an instance of Ollama that is accessible by your Paperless instance, or an OpenAI account, with paid API access.

## Installation in Paperless NGX

**Download or checkout the source code:**

* Copy the directory into your paperless docker compose directory (where the `docker-compose.yml` is located).

```bash
# It will look like this
user@host:~/paperless$ tree . -L 2
.
├── consume
├── docker-compose.env
├── docker-compose.yml
├── export
└── ngx-renamer
    ├── change_title.py
    ├── modules
    ├── LICENSE
    ├── placeholder.env
    ├── post_consume_script.sh
    ├── README.md
    ├── requirements.txt
    ├── settings.yaml
    ├── setup_venv.sh
    ├── test_pdf.py
    ├── test_title.py
    ├── test_document.py
```

**Edit placeholder.env and rename to `.env` in the `ngx-renamer` directory and put your credentials in:**

Follow the instructions in the file and replace the values with your credentials and URLs for Paperless as well as your OpenAI API key and other specified information.

**Open the `docker-compose.yml` file and add the directory `ngx-renamer` as internal directory to the webserver container and `post_consume_script.sh` as post consumption script:**

```bash
  webserver:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    restart: unless-stopped
    depends_on:
      - db
      - broker
      - gotenberg
      - tika
    ports:
      - "8443:8000"
    volumes:
      - /data/paperless/data:/usr/src/paperless/data
      - /data/paperless/media:/usr/src/paperless/media
      - ./export:/usr/src/paperless/export
      - /data/paperless/consume:/usr/src/paperless/consume
      # this is the new volume for nxg-renamer - add this
      - /your/path/to/paperless/ngx-renamer:/usr/src/ngx-renamer
    env_file: docker-compose.env
    environment:
      PAPERLESS_REDIS: redis://broker:6379
      PAPERLESS_DBHOST: db
      PAPERLESS_TIKA_ENABLED: 1
      PAPERLESS_TIKA_GOTENBERG_ENDPOINT: http://gotenberg:3000
      PAPERLESS_TIKA_ENDPOINT: http://tika:9998
      # This is the post consumption script call - add this
      PAPERLESS_POST_CONSUME_SCRIPT: /usr/src/ngx-renamer/post_consume_script.sh
```
**Restart your paperless system:**
```bash
user@host:~/paperless$ docker compose down
[+] Running 6/6
 ✔ Container paperless-webserver-1  Removed  10.4s
 ✔ Container paperless-db-1         Removed   0.3s
 ✔ Container paperless-tika-1       Removed   0.3s
 ✔ Container paperless-broker-1     Removed   0.2s
 ✔ Container paperless-gotenberg-1  Removed  10.2s
 ✔ Network paperless_default        Removed   0.2s
user@host:~/paperless$ docker compose up -d
[+] Running 6/6
 ✔ Network paperless_default        Created   0.1s
 ✔ Container paperless-broker-1     Started   0.6s
 ✔ Container paperless-db-1         Started   0.6s
 ✔ Container paperless-gotenberg-1  Started   0.5s
 ✔ Container paperless-tika-1       Started   0.6s
 ✔ Container paperless-webserver-1  Started   0.7s
```

**To initialize the virtual python environment in the docker container you have to call `setup_venv.sh`once and after any update of the container image. Make sure that the scripts and files are accessible by `root`. Follow these steps:**

```bash
# Change owner to root
user@host:~/paperless$ sudo chown -R root ngx-renamer/
# Make scripts executable
user@host:~/paperless$ sudo chmod +x ngx-renamer/setup_venv.sh
user@host:~/paperless$ sudo chmod +x ngx-renamer/post_consume_script.sh
# run setup routine
user@host:~/paperless$ docker compose exec -u paperless webserver /usr/src/ngx-renamer/setup_venv.sh
```

**The result sould look like:**

```bash
# Shortened version of the output
user@khost:~/paperless$ docker compose exec -u paperless webserver /usr/src/ngx-renamer/setup_venv.sh
Setting up virtual environment...
OK
...
Downloading PyYAML-6.0.2-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (767 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 767.5/767.5 kB 5.7 MB/s eta 0:00:00
Installing collected packages: pyyaml
Successfully installed pyyaml-6.0.2
```

**Done! Post cosumption only start after Paperless NGX created a new document through uploads, consumptions, or mails.**

```bash
# This script should run with an 404 error.
user@host:~/paperless$ docker compose exec -u paperless webserver /usr/src/ngx-renamer/post_consume_script.sh
```

## The settings

**Choosing a model**
First, you need to decide if you want to use OpenAI or Ollama. You can control this by setting the `model` value. You have two options, `ollama` or `openAi` (case sensitive).
Example:
```yaml
model: "ollama" # the base model to use, options are ollama or openai
```

**Model settings**
You will next need to set the `openai_model` and/or `ollama_model`  version. For example, if you are using Ollama, maybe you want to use `llama3.2:3b`.

```yaml
opennai_model: "gpt-4o-mini" # the model to use for the generation if model is set to openai
ollama_model: "llama3.2:3b" # the model to use for the generation
```

Please note that if you are using Ollama, some models may have unexpected results that will break this integration. For instance, Qwen3 is a really great model, with its thinking capability. However, it always returns `<think>``</think>` tags, even if you disable thinking in your prompt. So you would need to modify the code to strip these out (I did not bother with this, might look at it later, because it is a neat model)

**If you are using Ollama, set the URL**
You will need to set the URL to Ollama. Note that this is to the `serve` function and not the web ui, if you are using Open WebUI or something similar. These are different ports, and Ollama is most likely running on 11434, but check your install

```yaml
ollama_url: "http://localhost:11434" # the URL of the Ollama server with NO trailing slash
```

**A few notes about running Ollama**
You only need the base URL to the API, the code includes the \api\ and other parts of the call, so just include the URL/port

If you are doing reverse proxy or have your Ollama on a separate server with a distinct URL that redirects the URL to the right port, you may not need the port number.

If you are having trouble connecting to Ollama on a local machine OTHER than your Paperless-ngx machine, you might need to `serve` Ollama so that it is not just running on localhost but is open to any incoming traffic (also check your firewall/portforwarding). Learn more here: [Learn more about exposing Ollama API](https://aident.ai/blog/how-to-expose-ollama-service-api-to-network)

**Test the different models at OpenAI:**
```yaml
openai_model: "gpt-4o-mini" # the model to use for the generation
```
**Decide whether you want to have a date as a prefix:**
```yaml
with_date: true # boolean if the title should the date as a prefix
```
**Play with the prompt - it is a work in progress and tested in Englsh only:**
You may edit `settings.yaml` to edit the prompt and with that the results. I have found good success with the version of the prompt I have here, but you may want to change things, and different models may react differently.
```yaml
prompt:
  # the main prompt for the AI
  main: |
    - The following is the content from a PDF document generated with OCR. This PDF needs a new file name.
    - The file's content begins with: ###FILE CONTENT BEGIN###
    - The file's content ends with: ###FILE CONTENT END###
    - Based on the content, generate a concise, informative title that would help a user understand what is in the file when browsing through a directory.
    - Try to follow the following naming convention (words in the {} placeholder content should be separated by dashes): {DATE}_{AUTHOR}_{SHORT_TITLE}_{TYPE}
    -- Where {DATE}" date of creation or receipt, {AUTHOR}: the sender, author or source of the document, {SHORT_TITLE}: short, concise descriptive title, {TYPE}: one or two words describing the type of document it is
    -- Example: 2025-05-21_Fred-Meyers_Groceries-and-clothes_Receipt
    - Remove all stop words from the title
    - Ensure the title is unique and free of duplicate information
    - Keep the title under 127 characters
    - Never use punctuation or spaces in the title, other than underscores and dashes
    - Optimize the title for readability
    - Check the title against filename conventions
    - Re-read and further optimize the title if necessary
    - The filename must have more than just the date
    - Because this filename may be used in multiple filesystems, avoid special characters, such as slashes, commas, periods, asterisks, etc. that may not work with Linux, Windows or Macos
    - DO NOT USE COMMAS or PERIODS in the file name
    Your response should be a single line, no punctuation other than dashes or underscores, no explanation or other information is necessary. The response will be used in the filename directly.
  # the prompt part will be appended if the date should be included in the title using with_date: true
  with_date: |
    * analyze the text and find the date of the document
    * add the found date in form YYYY-MM-DD as a prefix to the doument title
    * if there is no date information in the document, use {current_date}
    * use the form: date sender title
  # the prompt part will be appended if the date should not be included in the title using with_date: false
  no_date: |
    * use the form: sender title
  # the prompt before the content of the document will be appended
  pre_content: |
    ###FILE CONTENT BEGIN###
  # the prompt after the content of the document will be appended
  post_content: |  
    ###FILE CONTENT END###
```

## Python development and testing

If you want to develop and test is without integrating it in Paperless NGX you can do that.

* Create a virtual environment
* Load all libraries
* Call test scripts
* Enjoy optimizing the prompt in settings.yaml

### Create virtual environment

```bash
# python or python3 is up to your system
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### Load all needed libraries

```bash
(.venv)$ pip install -r requirements.txt
```

### Call test scripts

```bash
# prints the thought title from a american law text
(.venv)$ python3 test_title.py
````

```bash
# read the content from a OCR'ed pdf file
(.venv)$ python3 ./test_pdf.py path/to/your/ocr-ed/pdf/file
