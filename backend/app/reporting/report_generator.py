from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


class ReportGenerator:
    @staticmethod
    def generate(atlas_result, output_path: str):
        """
        Generate a professional PDF report from an AtlasResult.
        """

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(output_path))

        styles = getSampleStyleSheet()

        title_style = styles["Heading1"]
        title_style.alignment = TA_CENTER

        heading_style = styles["Heading2"]

        normal_style = styles["BodyText"]

        elements = []

        # --------------------------------------------------
        # Title
        # --------------------------------------------------

        elements.append(
            Paragraph(
                "ATLAS Infrastructure Intelligence Report",
                title_style,
            )
        )

        elements.append(Spacer(1, 20))

        # --------------------------------------------------
        # Segmentation
        # --------------------------------------------------

        elements.append(
            Paragraph(
                "Segmentation",
                heading_style,
            )
        )

        seg = atlas_result.segmentation

        segmentation_table = Table(
            [
                ["Model", seg.model_name],
                [
                    "Inference Time",
                    f"{seg.inference_time_ms:.2f} ms",
                ],
                [
                    "Image Size",
                    f"{seg.image_size[0]} × {seg.image_size[1]}",
                ],
                [
                    "Mask Size",
                    f"{seg.mask.shape[0]} × {seg.mask.shape[1]}",
                ],
            ],
            colWidths=[160, 260],
        )

        segmentation_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(segmentation_table)

        elements.append(Spacer(1, 20))

        # --------------------------------------------------
        # Graph
        # --------------------------------------------------

        elements.append(
            Paragraph(
                "Topology",
                heading_style,
            )
        )

        graph_table = Table(
            [
                [
                    "Nodes",
                    atlas_result.topology_graph.number_of_nodes(),
                ],
                [
                    "Edges",
                    atlas_result.topology_graph.number_of_edges(),
                ],
            ],
            colWidths=[160, 260],
        )

        graph_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(graph_table)

        elements.append(Spacer(1, 20))

        # --------------------------------------------------
        # Risk
        # --------------------------------------------------

        elements.append(
            Paragraph(
                "Risk Assessment",
                heading_style,
            )
        )

        risk = atlas_result.risk

        risk_table = Table(
            [
                ["ARI", f"{risk['ari']:.3f}"],
                ["Risk Level", risk["level"]],
                [
                    "Recommendation",
                    atlas_result.recommendation,
                ],
            ],
            colWidths=[160, 260],
        )

        risk_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(risk_table)

        elements.append(Spacer(1, 20))

        # --------------------------------------------------
        # Simulation
        # --------------------------------------------------

        elements.append(
            Paragraph(
                "Simulation",
                heading_style,
            )
        )

        sim = atlas_result.simulation

        simulation_table = Table(
            [
                ["Scenario", sim.scenario],
                ["Removed Nodes", len(sim.removed_nodes)],
                ["Remaining Nodes", sim.remaining_nodes],
                ["Remaining Edges", sim.remaining_edges],
                ["Connected Components", sim.connected_components],
                ["Largest Component", sim.largest_component],
                ["Critical Node", str(sim.critical_node)],
            ],
            colWidths=[160, 260],
        )
        simulation_table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(simulation_table)

        elements.append(Spacer(1, 20))

        elements.append(
            Paragraph(
                "Generated by Project ATLAS",
                normal_style,
            )
        )

        doc.build(elements)

        return output_path