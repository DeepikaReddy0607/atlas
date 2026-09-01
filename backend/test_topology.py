import cv2
import numpy as np

from app.engines.analysis.skeleton import Skeletonizer
from app.engines.analysis.graph_builder import GraphBuilder
from app.engines.analysis.topology import TopologyBuilder


def analyze_topology(mask):
    """
    Convert a binary road mask into the ATLAS
    skeleton -> pixel graph -> topology graph pipeline.
    """

    # Ensure binary uint8 mask.
    binary = (
        mask > 0
    ).astype(
        np.uint8
    ) * 255

    # --------------------------------------------------------
    # Connected components on road mask
    # --------------------------------------------------------

    num_components, labels, stats, _ = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8,
        )
    )

    component_sizes = stats[
        1:, cv2.CC_STAT_AREA
    ]

    if len(component_sizes) > 0:

        largest_component = int(
            component_sizes.max()
        )

        total_road_pixels = int(
            component_sizes.sum()
        )

        largest_component_ratio = (
            largest_component
            / total_road_pixels
            if total_road_pixels > 0
            else 0.0
        )

    else:

        largest_component = 0
        total_road_pixels = 0
        largest_component_ratio = 0.0

    # --------------------------------------------------------
    # ATLAS graph pipeline
    # --------------------------------------------------------

    skeleton = Skeletonizer.build(
        binary
    )

    graph = GraphBuilder.build(
        skeleton
    )

    topology = TopologyBuilder.build(
        graph
    )

    # --------------------------------------------------------
    # Skeleton statistics
    # --------------------------------------------------------

    skeleton_pixels = int(
        np.count_nonzero(
            skeleton
        )
    )

    # --------------------------------------------------------
    # Topology statistics
    # --------------------------------------------------------

    topology_nodes = int(
        topology.number_of_nodes()
    )

    topology_edges = int(
        topology.number_of_edges()
    )

    # --------------------------------------------------------
    # Degree statistics
    # --------------------------------------------------------

    degrees = [
        degree
        for _, degree
        in topology.degree()
    ]

    dead_ends = sum(
        degree == 1
        for degree in degrees
    )

    junctions = sum(
        degree >= 3
        for degree in degrees
    )

    isolated_nodes = sum(
        degree == 0
        for degree in degrees
    )

    return {
        "road_pixels":
            total_road_pixels,

        "connected_components":
            max(
                0,
                num_components - 1,
            ),

        "largest_component":
            largest_component,

        "largest_component_ratio":
            largest_component_ratio,

        "skeleton_pixels":
            skeleton_pixels,

        "topology_nodes":
            topology_nodes,

        "topology_edges":
            topology_edges,

        "dead_ends":
            dead_ends,

        "junctions":
            junctions,

        "isolated_nodes":
            isolated_nodes,
    }


# ============================================================
# TEST
# ============================================================

mask = cv2.imread(
    "data/sample/roads_gt.png",
    cv2.IMREAD_GRAYSCALE,
)

if mask is None:

    raise RuntimeError(
        "Could not load "
        "data/sample/roads_gt.png"
    )

metrics = analyze_topology(
    mask
)

print()
print("=" * 60)
print("ATLAS TOPOLOGY DEBUG")
print("=" * 60)

binary = (
    mask > 0
).astype(
    np.uint8
) * 255

skeleton = Skeletonizer.build(
    binary
)

graph = GraphBuilder.build(
    skeleton
)

topology = TopologyBuilder.build(
    graph
)

print(
    f"Mask pixels       : "
    f"{np.count_nonzero(binary)}"
)

print(
    f"Skeleton pixels    : "
    f"{np.count_nonzero(skeleton)}"
)

print(
    f"Pixel graph nodes  : "
    f"{graph.number_of_nodes()}"
)

print(
    f"Pixel graph edges  : "
    f"{graph.number_of_edges()}"
)

print(
    f"Topology nodes     : "
    f"{topology.number_of_nodes()}"
)

print(
    f"Topology edges     : "
    f"{topology.number_of_edges()}"
)

print()
print("First pixel-graph nodes:")

for node in list(graph.nodes())[:10]:

    print(
        node,
        "degree=",
        graph.degree(node)
    )

print()
print("First topology nodes:")

for node in list(
    topology.nodes()
)[:10]:

    print(
        node,
        "degree=",
        topology.degree(node)
    )

print()
print("Topology edges:")

for u, v, data in topology.edges(
    data=True
):

    print(
        f"{u} -> {v} | "
        f"length={data.get('length')} | "
        f"pixels={len(data.get('pixels', []))}"
    )
print("=" * 60)