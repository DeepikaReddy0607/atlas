from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


class ReportGenerator:
    """
    Professional ATLAS Infrastructure Intelligence report generator.

    The public interface intentionally remains:

        ReportGenerator.generate(atlas_result, output_path)

    so existing API/frontend integrations do not need to change.
    """

    # ---------------------------------------------------------
    # ATLAS PALETTE
    # ---------------------------------------------------------

    BG = colors.HexColor("#07110D")
    PANEL = colors.HexColor("#0D1A15")
    PANEL_LIGHT = colors.HexColor("#12231C")

    GREEN = colors.HexColor("#49D17D")
    GREEN_DARK = colors.HexColor("#1D6B42")

    BLUE = colors.HexColor("#4FA3FF")
    AMBER = colors.HexColor("#E7B85C")
    RED = colors.HexColor("#E85D5D")

    TEXT = colors.HexColor("#E8F0E8")
    TEXT_MUTED = colors.HexColor("#9BAAA2")
    BORDER = colors.HexColor("#284438")

    WHITE = colors.white

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _safe(value, fallback="—"):
        return fallback if value is None else value

    @staticmethod
    def _format_number(value):
        if value is None:
            return "—"

        if isinstance(value, float):
            return f"{value:.3f}"

        return str(value)

    @staticmethod
    def _risk_color(level):
        level = str(level or "").upper()

        if level == "CRITICAL":
            return ReportGenerator.RED

        if level == "HIGH":
            return colors.HexColor("#F28C28")

        if level == "MODERATE":
            return ReportGenerator.AMBER

        if level == "LOW":
            return ReportGenerator.GREEN

        return ReportGenerator.TEXT_MUTED

    # ---------------------------------------------------------
    # STYLES
    # ---------------------------------------------------------

    @classmethod
    def _styles(cls):
        return {
            "cover_title": ParagraphStyle(
                "ATLASCoverTitle",
                fontName="Helvetica-Bold",
                fontSize=28,
                leading=32,
                textColor=cls.TEXT,
                alignment=TA_LEFT,
                spaceAfter=8,
            ),
            "cover_subtitle": ParagraphStyle(
                "ATLASCoverSubtitle",
                fontName="Helvetica",
                fontSize=11,
                leading=16,
                textColor=cls.TEXT_MUTED,
            ),
            "section": ParagraphStyle(
                "ATLASSection",
                fontName="Helvetica-Bold",
                fontSize=17,
                leading=21,
                textColor=cls.TEXT,
                spaceAfter=10,
            ),
            "section_small": ParagraphStyle(
                "ATLASSectionSmall",
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=cls.GREEN,
                uppercase=True,
            ),
            "body": ParagraphStyle(
                "ATLASBody",
                fontName="Helvetica",
                fontSize=9.5,
                leading=14,
                textColor=cls.TEXT_MUTED,
            ),
            "body_dark": ParagraphStyle(
                "ATLASBodyDark",
                fontName="Helvetica",
                fontSize=9,
                leading=13,
                textColor=colors.HexColor("#24352C"),
            ),
            "metric": ParagraphStyle(
                "ATLASMetric",
                fontName="Helvetica-Bold",
                fontSize=17,
                leading=20,
                textColor=cls.TEXT,
                alignment=TA_CENTER,
            ),
            "metric_label": ParagraphStyle(
                "ATLASMetricLabel",
                fontName="Helvetica",
                fontSize=7.5,
                leading=10,
                textColor=cls.TEXT_MUTED,
                alignment=TA_CENTER,
            ),
            "table_header": ParagraphStyle(
                "ATLASTableHeader",
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=cls.TEXT,
            ),
            "table_body": ParagraphStyle(
                "ATLASTableBody",
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                textColor=cls.TEXT,
            ),
            "risk": ParagraphStyle(
                "ATLASRisk",
                fontName="Helvetica-Bold",
                fontSize=21,
                leading=24,
                alignment=TA_CENTER,
            ),
        }

    # ---------------------------------------------------------
    # PAGE DECORATION
    # ---------------------------------------------------------

    @classmethod
    def _draw_page(cls, canvas, doc):
        canvas.saveState()

        width, height = A4

        # Page background
        canvas.setFillColor(cls.BG)
        canvas.rect(0, 0, width, height, fill=1, stroke=0)

        # Top technical line
        canvas.setStrokeColor(cls.BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(
            18 * mm,
            height - 17 * mm,
            width - 18 * mm,
            height - 17 * mm,
        )

        # Header
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(cls.GREEN)
        canvas.drawString(
            18 * mm,
            height - 12 * mm,
            "ATLAS",
        )

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(cls.TEXT_MUTED)
        canvas.drawRightString(
            width - 18 * mm,
            height - 12 * mm,
            "INFRASTRUCTURE INTELLIGENCE",
        )

        # Footer
        canvas.setStrokeColor(cls.BORDER)
        canvas.line(
            18 * mm,
            14 * mm,
            width - 18 * mm,
            14 * mm,
        )

        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(cls.TEXT_MUTED)

        canvas.drawString(
            18 * mm,
            9 * mm,
            "PROJECT ATLAS  /  AUTONOMOUS TERRAIN LEARNING & ANALYSIS SYSTEM",
        )

        canvas.drawRightString(
            width - 18 * mm,
            9 * mm,
            f"PAGE {doc.page}",
        )

        canvas.restoreState()

    # ---------------------------------------------------------
    # SECTION HEADER
    # ---------------------------------------------------------

    @classmethod
    def _section_header(cls, number, title, styles):
        return [
            Paragraph(
                f"{number:02d}  /  {title.upper()}",
                styles["section_small"],
            ),
            Spacer(1, 3 * mm),
        ]

    # ---------------------------------------------------------
    # METRIC CARD
    # ---------------------------------------------------------

    @classmethod
    def _metric_card(cls, label, value, styles):
        table = Table(
            [
                [
                    Paragraph(
                        str(value),
                        styles["metric"],
                    )
                ],
                [
                    Paragraph(
                        label.upper(),
                        styles["metric_label"],
                    )
                ],
            ],
            colWidths=[39 * mm],
            rowHeights=[11 * mm, 8 * mm],
        )

        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), cls.PANEL),
                    ("BOX", (0, 0), (-1, -1), 0.6, cls.BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        return table

    # ---------------------------------------------------------
    # DATA TABLE
    # ---------------------------------------------------------

    @classmethod
    def _data_table(cls, rows, styles, widths=None):
        formatted = []

        for index, row in enumerate(rows):
            formatted_row = []

            for value in row:
                style = (
                    styles["table_header"]
                    if index == 0
                    else styles["table_body"]
                )

                formatted_row.append(
                    Paragraph(
                        str(cls._safe(value)),
                        style,
                    )
                )

            formatted.append(formatted_row)

        table = Table(
            formatted,
            colWidths=widths,
            repeatRows=1,
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        cls.GREEN_DARK,
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        cls.TEXT,
                    ),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        cls.PANEL,
                    ),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [cls.PANEL, cls.PANEL_LIGHT],
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.35,
                        cls.BORDER,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        return table

    # ---------------------------------------------------------
    # GENERATE
    # ---------------------------------------------------------

    @classmethod
    def generate(cls, atlas_result, output_path: str):
        """
        Generate a professional ATLAS Infrastructure Intelligence PDF.
        """

        output_path = Path(output_path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        # --------------------------------------------------
        # Normalized ATLAS metrics
        # --------------------------------------------------

        seg = atlas_result.segmentation
        risk = atlas_result.risk
        resilience = atlas_result.resilience
        topology = atlas_result.topology_graph
        simulation = atlas_result.simulation

        connected_components = resilience.get(
            "connected_components", 0
        )

        largest_component = resilience.get(
            "largest_component", 0
        )

        critical_node = resilience.get(
            "critical_node"
        )

        styles = cls._styles()

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=24 * mm,
            bottomMargin=20 * mm,
            title="ATLAS Infrastructure Intelligence Report",
            author="Project ATLAS",
            subject="AI-powered road network infrastructure assessment",
        )

        elements = []

        # =====================================================
        # EXTRACT RESULTS
        # =====================================================

        segmentation = getattr(
            atlas_result,
            "segmentation",
            None,
        )

        topology = getattr(
            atlas_result,
            "topology_graph",
            None,
        )

        risk = getattr(
            atlas_result,
            "risk",
            {},
        ) or {}

        simulation = getattr(
            atlas_result,
            "simulation",
            None,
        )

        recommendation = getattr(
            atlas_result,
            "recommendation",
            None,
        )

        # =====================================================
        # COVER
        # =====================================================

        elements.append(Spacer(1, 25 * mm))

        elements.append(
            Paragraph(
                "ATLAS",
                ParagraphStyle(
                    "CoverBrand",
                    fontName="Helvetica-Bold",
                    fontSize=13,
                    textColor=cls.GREEN,
                    spaceAfter=8,
                ),
            )
        )

        elements.append(
            Paragraph(
                "Infrastructure<br/>Intelligence Report",
                styles["cover_title"],
            )
        )

        elements.append(
            Paragraph(
                "Autonomous Terrain Learning & Analysis System",
                styles["cover_subtitle"],
            )
        )

        elements.append(Spacer(1, 18 * mm))

        # Risk block
        risk_level = str(
            risk.get("level", "UNKNOWN")
        ).upper()

        risk_color = cls._risk_color(
            risk_level
        )

        risk_block = Table(
            [
                [
                    Paragraph(
                        "INFRASTRUCTURE RISK",
                        styles["section_small"],
                    )
                ],
                [
                    Paragraph(
                        risk_level,
                        ParagraphStyle(
                            "CoverRisk",
                            parent=styles["risk"],
                            textColor=risk_color,
                        ),
                    )
                ],
                [
                    Paragraph(
                        f"ARI  •  {cls._format_number(risk.get('ari'))}",
                        styles["body"],
                    )
                ],
            ],
            colWidths=[105 * mm],
            rowHeights=[9 * mm, 15 * mm, 9 * mm],
        )

        risk_block.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), cls.PANEL),
                    ("BOX", (0, 0), (-1, -1), 0.8, risk_color),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(risk_block)

        elements.append(Spacer(1, 16 * mm))

        generated_at = datetime.now().strftime(
            "%d %B %Y  •  %H:%M"
        )

        metadata = [
            ["REPORT TYPE", "Infrastructure Network Assessment"],
            ["GENERATED", generated_at],
            [
                "MODEL",
                cls._safe(
                    getattr(
                        segmentation,
                        "model_name",
                        None,
                    )
                ),
            ],
            [
                "ANALYSIS STATUS",
                "COMPLETED",
            ],
        ]

        elements.append(
            cls._data_table(
                metadata,
                styles,
                widths=[45 * mm, 105 * mm],
            )
        )

        elements.append(Spacer(1, 15 * mm))

        elements.append(
            Paragraph(
                "ATLAS transforms satellite imagery into an interpretable "
                "road-network representation, evaluates infrastructure "
                "resilience, identifies critical network elements, and "
                "simulates failure scenarios.",
                styles["body"],
            )
        )

        elements.append(PageBreak())

        # =====================================================
        # 01 — EXECUTIVE ASSESSMENT
        # =====================================================

        elements.extend(
            cls._section_header(
                1,
                "Executive Assessment",
                styles,
            )
        )

        nodes = (
            topology.number_of_nodes()
            if topology is not None
            else None
        )

        edges = (
            topology.number_of_edges()
            if topology is not None
            else None
        )

        critical_node = resilience.get(
            "critical_node"
        )

        if critical_node is None and simulation:
            critical_node = getattr(
                simulation,
                "critical_node",
                None,
            )

        summary_text = (
            f"ATLAS identified a road network containing "
            f"<b>{cls._safe(nodes)}</b> topology nodes and "
            f"<b>{cls._safe(edges)}</b> network connections. "
            f"The calculated Adaptive Resilience Index (ARI) is "
            f"<b>{cls._format_number(risk.get('ari'))}</b>, "
            f"corresponding to a <b>{risk_level}</b> infrastructure "
            f"risk classification."
        )

        elements.append(
            Paragraph(
                summary_text,
                styles["body"],
            )
        )

        elements.append(Spacer(1, 8 * mm))

        metric_row = Table(
            [
                [
                    cls._metric_card(
                        "Topology Nodes",
                        cls._safe(nodes),
                        styles,
                    ),
                    cls._metric_card(
                        "Network Edges",
                        cls._safe(edges),
                        styles,
                    ),
                    cls._metric_card(
                        "ARI",
                        cls._format_number(
                            risk.get("ari")
                        ),
                        styles,
                    ),
                ]
            ],
            colWidths=[
                45 * mm,
                45 * mm,
                45 * mm,
            ],
        )

        metric_row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        elements.append(metric_row)

        elements.append(Spacer(1, 10 * mm))

        assessment_rows = [
            ["ASSESSMENT", "RESULT"],
            [
                "Risk classification",
                risk_level,
            ],
            [
                "Critical network element",
                str(cls._safe(critical_node)),
            ],
            [
                "Connected components",
                cls._safe(
                    connected_components
                ),
            ],
            [
                "Largest component",
                cls._safe(
                    largest_component
                ),
            ],
        ]

        elements.append(
            cls._data_table(
                assessment_rows,
                styles,
                widths=[70 * mm, 80 * mm],
            )
        )

        elements.append(Spacer(1, 10 * mm))

        elements.append(
            Paragraph(
                "<b>ATLAS interpretation:</b> "
                + str(
                    cls._safe(
                        recommendation,
                        "No recommendation available.",
                    )
                ),
                styles["body"],
            )
        )

        elements.append(PageBreak())

        # =====================================================
        # 02 — AI VISION
        # =====================================================

        elements.extend(
            cls._section_header(
                2,
                "AI Vision Analysis",
                styles,
            )
        )

        image_size = getattr(
            segmentation,
            "image_size",
            None,
        )

        mask = getattr(
            segmentation,
            "mask",
            None,
        )

        mask_size = None

        if mask is not None:
            try:
                mask_size = (
                    mask.shape[0],
                    mask.shape[1],
                )
            except Exception:
                pass

        vision_rows = [
            ["PARAMETER", "VALUE"],
            [
                "Vision model",
                cls._safe(
                    getattr(
                        segmentation,
                        "model_name",
                        None,
                    )
                ),
            ],
            [
                "Inference time",
                (
                    f"{segmentation.inference_time_ms:.2f} ms"
                    if segmentation
                    and getattr(
                        segmentation,
                        "inference_time_ms",
                        None,
                    )
                    is not None
                    else "—"
                ),
            ],
            [
                "Input image",
                (
                    f"{image_size[0]} × {image_size[1]} px"
                    if image_size
                    else "—"
                ),
            ],
            [
                "Segmentation mask",
                (
                    f"{mask_size[0]} × {mask_size[1]} px"
                    if mask_size
                    else "—"
                ),
            ],
        ]

        elements.append(
            cls._data_table(
                vision_rows,
                styles,
                widths=[70 * mm, 80 * mm],
            )
        )

        elements.append(Spacer(1, 10 * mm))

        elements.append(
            Paragraph(
                "The ATLAS vision stage converts the input satellite "
                "imagery into a binary road representation. This output "
                "forms the foundation for subsequent skeletonization, "
                "graph construction, topology analysis, and resilience "
                "assessment.",
                styles["body"],
            )
        )

        elements.append(Spacer(1, 8 * mm))

        pipeline_rows = [
            ["PIPELINE STAGE", "OUTPUT"],
            [
                "Satellite imagery",
                "Input geospatial scene",
            ],
            [
                "Road segmentation",
                "Binary road mask",
            ],
            [
                "Skeletonization",
                "Centerline representation",
            ],
            [
                "Graph construction",
                "Pixel / topology graph",
            ],
            [
                "Criticality analysis",
                "Priority network elements",
            ],
        ]

        elements.append(
            cls._data_table(
                pipeline_rows,
                styles,
                widths=[70 * mm, 80 * mm],
            )
        )

        elements.append(PageBreak())

        # =====================================================
        # 03 — NETWORK TOPOLOGY
        # =====================================================

        elements.extend(
            cls._section_header(
                3,
                "Road Network & Topology",
                styles,
            )
        )

        topology_rows = [
            ["NETWORK METRIC", "VALUE"],
            [
                "Topology nodes",
                cls._safe(nodes),
            ],
            [
                "Topology edges",
                cls._safe(edges),
            ],
        ]

        elements.append(
            cls._data_table(
                topology_rows,
                styles,
                widths=[70 * mm, 80 * mm],
            )
        )

        elements.append(Spacer(1, 10 * mm))

        elements.append(
            Paragraph(
                "The extracted road skeleton is represented as a graph "
                "where nodes describe meaningful network junctions or "
                "endpoints and edges describe road connections between "
                "them. This representation allows ATLAS to evaluate "
                "connectivity and failure propagation computationally.",
                styles["body"],
            )
        )

        elements.append(Spacer(1, 10 * mm))

        topology_summary = [
            [
                cls._metric_card(
                    "Nodes",
                    cls._safe(nodes),
                    styles,
                ),
                cls._metric_card(
                    "Edges",
                    cls._safe(edges),
                    styles,
                ),
            ]
        ]

        topology_summary_table = Table(
            topology_summary,
            colWidths=[65 * mm, 65 * mm],
        )

        topology_summary_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        elements.append(
            topology_summary_table
        )

        elements.append(PageBreak())

        # =====================================================
        # 04 — RESILIENCE & RISK
        # =====================================================

        elements.extend(
            cls._section_header(
                4,
                "Resilience & Risk Assessment",
                styles,
            )
        )

        ari = risk.get("ari")

        risk_rows = [
            ["RISK INDICATOR", "ASSESSMENT"],
            [
                "Adaptive Resilience Index",
                cls._format_number(ari),
            ],
            [
                "Risk level",
                risk_level,
            ],
            [
                "Critical node",
                str(cls._safe(critical_node)),
            ],
        ]

        elements.append(
            cls._data_table(
                risk_rows,
                styles,
                widths=[70 * mm, 80 * mm],
            )
        )

        elements.append(Spacer(1, 10 * mm))

        risk_panel = Table(
            [
                [
                    Paragraph(
                        "ATLAS RISK CLASSIFICATION",
                        styles["section_small"],
                    )
                ],
                [
                    Paragraph(
                        risk_level,
                        ParagraphStyle(
                            "RiskLarge",
                            parent=styles["risk"],
                            textColor=risk_color,
                        ),
                    )
                ],
                [
                    Paragraph(
                        (
                            "Network condition requires attention "
                            "according to the computed resilience "
                            "assessment."
                            if risk_level in {"HIGH", "CRITICAL"}
                            else
                            "Network currently exhibits a lower "
                            "computed infrastructure risk profile."
                        ),
                        styles["body"],
                    )
                ],
            ],
            colWidths=[150 * mm],
        )

        risk_panel.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), cls.PANEL),
                    ("BOX", (0, 0), (-1, -1), 0.8, risk_color),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )

        elements.append(risk_panel)

        elements.append(Spacer(1, 10 * mm))

        elements.append(
            Paragraph(
                "<b>Recommended action:</b> "
                + str(
                    cls._safe(
                        recommendation,
                        "No specific recommendation was generated.",
                    )
                ),
                styles["body"],
            )
        )

        elements.append(PageBreak())

        # =====================================================
        # 05 — FAILURE SIMULATION
        # =====================================================

        elements.extend(
            cls._section_header(
                5,
                "Failure Simulation",
                styles,
            )
        )

        if simulation is not None:
            sim_scenario = getattr(
                simulation,
                "scenario",
                None,
            )

            removed_nodes = getattr(
                simulation,
                "removed_nodes",
                [],
            ) or []

            removed_edges = getattr(
                simulation,
                "removed_edges",
                [],
            ) or []

            simulation_rows = [
                ["SIMULATION METRIC", "RESULT"],
                [
                    "Scenario",
                    cls._safe(sim_scenario),
                ],
                [
                    "Removed nodes",
                    len(removed_nodes),
                ],
                [
                    "Removed edges",
                    len(removed_edges),
                ],
                [
                    "Original nodes",
                    cls._safe(
                        getattr(
                            simulation,
                            "original_nodes",
                            None,
                        )
                    ),
                ],
                [
                    "Original edges",
                    cls._safe(
                        getattr(
                            simulation,
                            "original_edges",
                            None,
                        )
                    ),
                ],
                [
                    "Remaining nodes",
                    cls._safe(
                        getattr(
                            simulation,
                            "remaining_nodes",
                            None,
                        )
                    ),
                ],
                [
                    "Remaining edges",
                    cls._safe(
                        getattr(
                            simulation,
                            "remaining_edges",
                            None,
                        )
                    ),
                ],
                [
                    "Connected components",
                    cls._safe(
                        getattr(
                            simulation,
                            "connected_components",
                            None,
                        )
                    ),
                ],
                [
                    "Largest component",
                    cls._safe(
                        getattr(
                            simulation,
                            "largest_component",
                            None,
                        )
                    ),
                ],
                [
                    "Critical node",
                    str(
                        cls._safe(
                            getattr(
                                simulation,
                                "critical_node",
                                None,
                            )
                        )
                    ),
                ],
            ]

            elements.append(
                cls._data_table(
                    simulation_rows,
                    styles,
                    widths=[75 * mm, 75 * mm],
                )
            )

            elements.append(Spacer(1, 10 * mm))

            elements.append(
                Paragraph(
                    "The simulation evaluates the network after "
                    "removing the selected failure element. Changes "
                    "in connectivity and component structure provide "
                    "an interpretable estimate of the potential "
                    "impact of infrastructure disruption.",
                    styles["body"],
                )
            )

        else:
            elements.append(
                Paragraph(
                    "No failure simulation result is currently "
                    "associated with this analysis.",
                    styles["body"],
                )
            )

        elements.append(PageBreak())

        # =====================================================
        # 06 — ENGINEERING RECOMMENDATION
        # =====================================================

        elements.extend(
            cls._section_header(
                6,
                "Engineering Recommendation",
                styles,
            )
        )

        recommendation_panel = Table(
            [
                [
                    Paragraph(
                        "ATLAS RECOMMENDATION",
                        styles["section_small"],
                    )
                ],
                [
                    Paragraph(
                        str(
                            cls._safe(
                                recommendation,
                                "No recommendation available.",
                            )
                        ),
                        styles["body"],
                    )
                ],
            ],
            colWidths=[150 * mm],
        )

        recommendation_panel.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), cls.PANEL),
                    ("BOX", (0, 0), (-1, -1), 0.7, cls.GREEN),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )

        elements.append(
            recommendation_panel
        )

        elements.append(Spacer(1, 12 * mm))

        elements.append(
            Paragraph(
                "Decision Support",
                styles["section_small"],
            )
        )

        elements.append(Spacer(1, 3 * mm))

        elements.append(
            Paragraph(
                "ATLAS is intended to support infrastructure "
                "assessment and prioritization by combining "
                "AI-based terrain interpretation with graph-based "
                "network analysis. The results should be interpreted "
                "alongside field observations, authoritative "
                "geospatial datasets, and engineering judgement "
                "before operational decisions are made.",
                styles["body"],
            )
        )

        elements.append(Spacer(1, 15 * mm))

        final_rows = [
            ["FINAL ATLAS ASSESSMENT", "VALUE"],
            [
                "Risk level",
                risk_level,
            ],
            [
                "ARI",
                cls._format_number(ari),
            ],
            [
                "Critical element",
                str(cls._safe(critical_node)),
            ],
            [
                "Network nodes",
                cls._safe(nodes),
            ],
            [
                "Network edges",
                cls._safe(edges),
            ],
        ]

        elements.append(
            cls._data_table(
                final_rows,
                styles,
                widths=[75 * mm, 75 * mm],
            )
        )

        elements.append(Spacer(1, 15 * mm))

        elements.append(
            Paragraph(
                "END OF REPORT  •  PROJECT ATLAS",
                ParagraphStyle(
                    "EndReport",
                    fontName="Helvetica-Bold",
                    fontSize=8,
                    textColor=cls.GREEN,
                    alignment=TA_CENTER,
                ),
            )
        )

        # =====================================================
        # BUILD
        # =====================================================

        doc.build(
            elements,
            onFirstPage=cls._draw_page,
            onLaterPages=cls._draw_page,
        )

        return output_path