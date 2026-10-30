
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from collections import deque

# ==========================================
# WUMPUS WORLD SETTINGS
# ==========================================

SIZE = 4

START = (3, 0)
GOLD = (3, 2)
WUMPUS = (0, 3)

PITS = {
    (0, 1),
    (1, 2),
    (2, 1)
}

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Wumpus World Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Wumpus World Agent")
st.caption("Intelligent Agent using BFS Path Finding")

st.markdown("""
Explore a 4×4 cave, collect the gold, and return safely
to the starting position.
""")

# ==========================================
# SESSION STATE
# ==========================================

if "agent" not in st.session_state:
    st.session_state.agent = START

if "running" not in st.session_state:
    st.session_state.running = False

if "mission" not in st.session_state:
    st.session_state.mission = False

if "route" not in st.session_state:
    st.session_state.route = []

if "step" not in st.session_state:
    st.session_state.step = 0

if "status" not in st.session_state:
    st.session_state.status = "Agent is ready."

if "history" not in st.session_state:
    st.session_state.history = []


# ==========================================
# FIND NEIGHBORING CELLS
# ==========================================

def get_neighbors(position):
    row, col = position
    neighbors = []

    if row > 0:
        neighbors.append((row - 1, col))

    if row < SIZE - 1:
        neighbors.append((row + 1, col))

    if col > 0:
        neighbors.append((row, col - 1))

    if col < SIZE - 1:
        neighbors.append((row, col + 1))

    return neighbors


# ==========================================
# PERCEPTS
# ==========================================

def has_stench(position):
    return WUMPUS in get_neighbors(position)


def has_breeze(position):
    return any(
        neighbor in PITS
        for neighbor in get_neighbors(position)
    )


def get_percepts(position):
    percepts = []

    if has_stench(position):
        percepts.append("Stench")

    if has_breeze(position):
        percepts.append("Breeze")

    if position == GOLD:
        percepts.append("Glitter")

    return percepts or ["Nothing detected"]


# ==========================================
# SAFE CELL CHECK
# ==========================================

def is_safe(position):
    return (
        position not in PITS
        and position != WUMPUS
    )


# ==========================================
# BFS PATH FINDING
# ==========================================

def find_path(start, target):
    queue = deque([[start]])
    visited = {start}

    while queue:
        path = queue.popleft()
        current = path[-1]

        if current == target:
            return path

        for neighbor in get_neighbors(current):
            if neighbor not in visited and is_safe(neighbor):
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return None


# ==========================================
# DISPLAY GRID
# ==========================================

def display_world():
    st.subheader("🗺️ Cave Environment")

    st.markdown("""
    <style>
    .cell {
        border: 2px solid #64748b;
        border-radius: 10px;
        padding: 15px 3px;
        min-height: 95px;
        text-align: center;
        font-size: 14px;
        margin: 3px 0;
    }
    .agent { background-color: #bbf7d0; color: #14532d; }
    .gold { background-color: #fef08a; color: #713f12; }
    .pit { background-color: #fecaca; color: #7f1d1d; }
    .wumpus { background-color: #e9d5ff; color: #581c87; }
    .empty { background-color: #e2e8f0; color: #334155; }
    </style>
    """, unsafe_allow_html=True)

    for row in range(SIZE):
        cols = st.columns(SIZE)

        for col in range(SIZE):
            position = (row, col)

            if position == st.session_state.agent:
                symbol, name, css = "🤖", "Agent", "agent"
            elif position == GOLD:
                symbol, name, css = "💰", "Gold", "gold"
            elif position == WUMPUS:
                symbol, name, css = "👹", "Wumpus", "wumpus"
            elif position in PITS:
                symbol, name, css = "🕳️", "Pit", "pit"
            else:
                symbol, name, css = "⬜", "Empty", "empty"

            cols[col].markdown(
                f'<div class="cell {css}">'
                f'<b>{symbol}</b><br>{name}<br>'
                f'({row}, {col})</div>',
                unsafe_allow_html=True
            )


# ==========================================
# START MISSION
# ==========================================

def start_mission():
    path_to_gold = find_path(START, GOLD)

    if not path_to_gold:
        st.session_state.status = "No safe path found!"
        return

    path_home = find_path(GOLD, START)

    if not path_home:
        st.session_state.status = "No safe return path found!"
        return

    # Combine outward and return paths
    complete_route = path_to_gold + path_home[1:]

    st.session_state.agent = START
    st.session_state.route = complete_route
    st.session_state.step = 0
    st.session_state.running = True
    st.session_state.mission = False
    st.session_state.history = [START]
    st.session_state.status = "Agent is moving toward Gold."


# ==========================================
# CONTROLS
# ==========================================

button1, button2 = st.columns(2)

with button1:
    if st.button(
        "▶️ START",
        use_container_width=True,
        disabled=st.session_state.running
    ):
        start_mission()
        st.rerun()

with button2:
    if st.button("🔄 RESET", use_container_width=True):
        st.session_state.agent = START
        st.session_state.running = False
        st.session_state.mission = False
        st.session_state.route = []
        st.session_state.step = 0
        st.session_state.history = []
        st.session_state.status = "Agent is ready."
        st.rerun()


# ==========================================
# AUTOMATIC AGENT MOVEMENT
# ==========================================

if st.session_state.running:
    st_autorefresh(
        interval=1000,
        limit=None,
        key="agent_refresh"
    )

    route = st.session_state.route

    if st.session_state.step < len(route) - 1:
        st.session_state.step += 1
        position = route[st.session_state.step]

        st.session_state.agent = position
        st.session_state.history.append(position)

        if position == GOLD:
            st.session_state.status = (
                "✨ Gold found! Returning to start..."
            )
        elif position == START:
            st.session_state.status = (
                "Mission completed! Agent returned safely."
            )
            st.session_state.running = False
            st.session_state.mission = True
        else:
            st.session_state.status = "Agent is exploring safely."

    else:
        st.session_state.status = (
            "Mission completed! Gold collected and agent returned."
        )
        st.session_state.running = False
        st.session_state.mission = True


# ==========================================
# DISPLAY RESULTS
# ==========================================

st.divider()

display_world()

st.subheader("📊 Agent Status")
st.info(st.session_state.status)

percepts = get_percepts(st.session_state.agent)
st.write("**Current Position:**", st.session_state.agent)
st.write("**Percepts:**", ", ".join(percepts))

if st.session_state.route:
    formatted_path = " → ".join(
        str(pos) for pos in st.session_state.route
    )
    st.write("**Complete Path:**", formatted_path)

if st.session_state.history:
    st.write("**Visited Cells:**", st.session_state.history)

if st.session_state.mission:
    st.success("🏆 MISSION COMPLETED!")
    