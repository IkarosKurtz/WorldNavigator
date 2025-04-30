import uuid
import streamlit as st
from pyvis.network import Network
import networkx as nx
import json
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

st.set_page_config(page_title="World Editor", layout="wide", page_icon="🗺️")

st.title("World Graph Editor")

if 'G' not in st.session_state:
  st.session_state.G = nx.DiGraph()
if 'locations' not in st.session_state:
  st.session_state.locations = {}
if 'location_name' not in st.session_state:
  st.session_state.location_name = ""
if 'is_indoor' not in st.session_state:
  st.session_state.is_indoor = True
if 'day_bg' not in st.session_state:
  st.session_state.day_bg = ""
if 'afternoon_bg' not in st.session_state:
  st.session_state.afternoon_bg = ""
if 'night_bg' not in st.session_state:
  st.session_state.night_bg = ""
if 'clear_form' not in st.session_state:
  st.session_state.clear_form = False

# Si clear_form es True, resetea variables antes de renderizar
if st.session_state.clear_form:
  st.session_state.location_name = ""
  st.session_state.is_indoor = True
  st.session_state.day_bg = ""
  st.session_state.afternoon_bg = ""
  st.session_state.night_bg = ""
  st.session_state.clear_form = False

note, _ = st.columns([2, 1])
with note:
  st.markdown(
    """
    This tool is intended to help you **create and visualize your own worlds***.
    It is still in development and may contain bugs or incomplete features.
    
    Please report any issues or suggestions on the [GitHub repository](https://github.com/IkarosKurtz/WorldNavigator/issues).
    """,
  )

form, graph = st.columns([.4, .6])

with form:
  col_add, col_connect = st.columns(2)

  with col_add:
    st.subheader("Add Location")
    with st.form(key='node_form'):
      name = st.text_input(
        "Location Name",
        placeholder="School",
        key='location_name'
      )
      is_indoor = st.checkbox(
        "Indoor?",
        key='is_indoor'
      )
      day_bg = st.text_input(
        "Background (day)",
        placeholder="bg_school",
        key='day_bg'
      )
      afternoon_bg = st.text_input(
        "Background (afternoon)",
        placeholder="bg_school_afternoon",
        key='afternoon_bg'
      )
      night_bg = st.text_input(
        "Background (night)",
        placeholder="bg_school_night",
        key='night_bg'
      )
      submitted = st.form_submit_button(
        "Add Location",
        type="primary",
      )

      if submitted:
        if not name or not day_bg:
          if not name:
            st.error("A name is required.")
          elif not day_bg:
            st.error("Day background is required.")
        else:
          node_id = str(uuid.uuid4())
          color = '#4A90E2' if is_indoor else '#7ED321'
          st.session_state.G.add_node(
            node_id,
            label=name,
            color=color,
            size=20
          )
          st.session_state.locations[node_id] = {
            "name": name,
            "is_indoor": is_indoor,
            "backgrounds": {
              "day": day_bg,
              "afternoon": afternoon_bg,
              "night": night_bg
            },
            "connected_locations": []
          }
          st.session_state.clear_form = True
          st.rerun()

  with col_connect:
    st.subheader("Connect Locations")
    if len(st.session_state.locations) >= 2:
      with st.form(key='edge_form'):
        nodes = list(st.session_state.G.nodes(data=True))
        nodes_dict = {node[1]['label']: node[0] for node in nodes}
        options = list(nodes_dict.keys())

        node_a = st.selectbox("From", options)
        node_b = st.selectbox("To", options)
        bidirectional = st.checkbox("Bidirectional?", value=True)

        if st.form_submit_button("Connect", type="primary"):
          from_id = nodes_dict[node_a]
          to_id = nodes_dict[node_b]
          st.session_state.G.add_edge(from_id, to_id, length=200, color='#fff')
          st.session_state.locations[from_id]["connected_locations"].append(
            st.session_state.locations[to_id]["name"] if bidirectional else {
              "name": st.session_state.locations[to_id]["name"],
              "one_way": True
            }
          )

          if bidirectional:
            st.session_state.G.add_edge(to_id, from_id, length=200, color='#fff')
    else:
      st.write("You need at least two locations to connect them.")

with graph:
  st.header("Your World")

  nt = Network(height="600px", directed=True, bgcolor="#434343", font_color="#fff")

  nt.from_nx(st.session_state.G)
  nt.show_buttons(filter_=['physics'])

  html_path = "./tmp/graph.html"
  nt.save_graph(html_path)

  with open(html_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

  soup = BeautifulSoup(html_content, 'html.parser')

  for tag in soup.find_all(['center', 'h1']):
    tag.decompose()

  body = soup.find('body')
  if body:
    style_tag = soup.new_tag('style')
    style_tag.string = (
      ".card { border: none !important; }"
      "#mynetwork { border: none !important; }"
    )
    body.insert(0, style_tag)

  html_content = str(soup)
  components.html(html_content, height=600)

edit, controls = st.columns([.6, .4])

with edit:
  st.header("Edit Location")

  if st.session_state.locations:
    loc_options = {v["name"]: k for k, v in st.session_state.locations.items()}
    selected_loc_name = st.selectbox("Select Location to Edit", list(loc_options.keys()))

    selected_id = loc_options[selected_loc_name]
    selected_loc = st.session_state.locations[selected_id]

    with st.form(key='edit_form'):
      new_name = st.text_input("New Name", value=selected_loc["name"])
      new_indoor = st.checkbox("Indoor?", value=selected_loc["is_indoor"])
      new_day_bg = st.text_input("Day Background", value=selected_loc["backgrounds"]["day"])
      new_afternoon_bg = st.text_input("Afternoon Background", value=selected_loc["backgrounds"]["afternoon"])
      new_night_bg = st.text_input("Night Background", value=selected_loc["backgrounds"]["night"])

      if 'success_message' in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message

      if st.form_submit_button("Save Changes"):
        selected_loc["name"] = new_name
        selected_loc["is_indoor"] = new_indoor
        selected_loc["backgrounds"]["day"] = new_day_bg
        selected_loc["backgrounds"]["afternoon"] = new_afternoon_bg
        selected_loc["backgrounds"]["night"] = new_night_bg
        st.session_state.G.nodes[selected_id]["label"] = new_name
        st.session_state.success_message = "Location updated."
        st.rerun()

with controls:
  st.header("Controls")
  world_name = st.text_input("World Name", value="My World")

  export, download, restart = st.columns([1, 1, 1])
  world_json = None

  with export:
    if st.button("Export", type='primary'):
      if not world_name or world_name == '':
        st.error("Please enter a world name.")
      else:
        world_json = {
          "name": world_name,
          "locations": list(st.session_state.locations.values())
        }

  with download:
    if world_json:
      st.download_button(
        label="Download JSON",
        data=json.dumps(world_json, indent=2),
        file_name=f"{world_name}.world.json",
        mime="application/json",
        type='primary'
      )

  with restart:
    if st.button("Restart"):
      st.session_state.G = nx.DiGraph()
      st.session_state.locations = {}
      st.session_state.form_submitted = False
      st.rerun()
