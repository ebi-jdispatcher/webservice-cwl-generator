# Web Service Clients CWL Generator

`cwlgenerator.py` allows auto-generation of Common Workflow Language (CWL) definitions for
Sample CLI Clients for
[EMBL-EBI's Job Dispatcher Web Service Bioinformatics Tools](https://www.ebi.ac.uk/services).

CWL generated with this program are uploaded to the [webservice-cwl](https://github.com/ebi-jdispatcher/webservice-cwl)
repository. These CWL require the actual clients or the *webservice-clients* Docker image from
 [webservice-clients](https://github.com/ebi-jdispatcher/webservice-clients) in order to run the
clients.

## How to use it

Download the source code or clone the repository:

```bash
git clone https://github.com/ebi-jdispatcher/webservice-cwl-generator.git
```

Specially if you have no root access to your machine, you might need to
use [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
Prepare a virtual environment where all the Python dependencies will be installed.
This project has been developed and tested with Python 3.6.5.

```bash
virtualenv -p `which python` env
source ./env/bin/activate
# deactivate
```

A full list of Python dependencies is provided in [requirements.txt](requirements.txt). Install dependencies with:

```bash
pip install --upgrade -r requirements.txt
```

Now run the program to generate python clients for all supported EBI tools, they will be placed in the `dist` folder.
All available clients are listed in [clients.ini](clients.ini).

## Generating CWL for the clients

Run the following commands to generate CWL using Python or Perl clients for all the Bioinformatics tools provided.

```bash
# based on python clients
python cwlgenerator.py python
```

```bash
# based on perl clients
python cwlgenerator.py perl
```

Alternatively, use `--client <client_name>` to get only a selected client.

```bash
python cwlgenerator.py python --client clustalo,ncbiblast
```

CWL can also run the clients with Docker by using the Docker image provided in the
[webservice-clients](https://www.ebi.ac.uk/services) repository. We can generate CWL with Docker
dependency by passing the `--docker` flag.

```bash
python cwlgenerator.py python --client clustalo,ncbiblast --docker
```

## Running the generated CWL with cwltool

### How to install cwltool

You will need cwl-runner ([cwltool](https://github.com/common-workflow-language/cwltool)) to run CWL
descriptions. Official instructions on how to install cwltool are provided in
https://github.com/common-workflow-language/cwltool

### Example using CWL with a Python client and Docker

An example test for Clustal Omega using the Python client:

```bash
cwltool dist/clustalo.cwl --email <your@email.com> --sequence sp:wap_rat,sp:wap_mouse,sp:wap_pig
```

## Documentation

More documentation about [EMBL-EBI Bioinformatics Web Services](https://www.ebi.ac.uk/jdispatcher/docs/webservices/)

## Contact and Support

If you have any problems, suggestions or comments for our services please
contact us via [EBI Support](https://www.ebi.ac.uk/about/contact/support/job-dispatcher-services).

## License
The European Bioinformatics Institute - [EMBL-EBI](https://www.ebi.ac.uk/), is an Intergovernmental Organization which, as part of the European Molecular Biology Laboratory family, focuses on research and services in bioinformatics.  

Apache License 2.0. See [license](LICENSE) for details.
