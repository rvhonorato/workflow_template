from IPython.core.display import display, HTML
import random
import hashlib
import json
from pathlib import Path
import re
import ipykernel
import requests

from requests.compat import urljoin
from notebook.notebookapp import list_running_servers

display(HTML(open("src/gromacs-training.css").read()))


def hide_toggle(for_next=False):
    this_cell = """$('div.cell.code_cell.rendered.selected')"""
    next_cell = this_cell + '.next()'

    toggle_text = 'Show/hide solution'  # text shown on toggle link
    target_cell = this_cell  # target cell to control with toggle
    js_hide_current = ''  # bit of JS to permanently hide code in current cell (only when toggling next cell)

    if for_next:
        target_cell = next_cell
        toggle_text += 'coming up'
        js_hide_current = this_cell + '.find("div.input").hide();'

    js_f_name = 'code_toggle_{}'.format(str(random.randint(1, 2**64)))

    html = """
        <script>
            function {f_name}() {{
                {cell_selector}.find('div.input').toggle();
            }}

            {js_hide_current}
        </script>

        <a href="javascript:{f_name}()">{toggle_text}</a>
    """.format(
        f_name=js_f_name,
        cell_selector=target_cell,
        js_hide_current=js_hide_current,
        toggle_text=toggle_text
    )

    return HTML(html)


def get_notebook_name():
    """Return the full path of the jupyter notebook."""
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)
    server_list = list_running_servers()
    for server in server_list:
        url = urljoin(server['url'], 'api/sessions')
        response = requests.get(url,
                                params={
                                    'token': server.get('token', '')
                                    })
        json_response = json.loads(response.text)
        for element in json_response:
            if element['kernel']['id'] == kernel_id:
                full_path = Path(server['notebook_dir'], element['notebook']['path'])
                return str(full_path)


def check_notebook():
    """"""
    notebook_name = get_notebook_name()

    # read in reference checksum
    nbpathhead, nbname = os.path.split(notebook_name)
    results = open(nbpathhead + '/src/.check/' + nbname + '.md5', 'r').read()
    checksum_reference = str(results.split()[0])

    # evaluate currrent checksum
    checksum_current = hashlib.md5(open(notebook_name, 'rb').read()).hexdigest()

    # report
    if checksum_current == checksum_reference:
        print("Notebook is unchanged from source")
    else:
        print("Notebook has been modified")
