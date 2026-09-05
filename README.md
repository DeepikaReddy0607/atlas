# ATLAS

## AI-Powered Geospatial Road Network Analysis & Resilience Platform

ATLAS is an end-to-end geospatial intelligence platform that transforms satellite imagery into an interpretable road-network model and evaluates how that network behaves under infrastructure failures.

Instead of stopping at road segmentation, ATLAS connects computer vision with graph-based topology and resilience analysis:

**Satellite Image → Road Segmentation → Skeletonization → Graph Construction → Criticality Analysis → Failure Simulation → Risk Assessment → Visualization & Reporting**

---

## Overview

Road networks extracted from satellite imagery can provide useful information for understanding connectivity, accessibility, and infrastructure vulnerability.

ATLAS was designed as a complete engineering pipeline that combines deep-learning-based road extraction with graph-based network analysis.

The system:

1. Accepts a satellite image as input.
2. Extracts road pixels using a deep-learning ensemble.
3. Converts the segmentation into a road skeleton.
4. Builds a graph representation of the road network.
5. Identifies structurally important nodes and edges.
6. Measures network resilience.
7. Simulates infrastructure failures.
8. Estimates the resulting network risk.
9. Presents the analysis through an interactive geospatial workstation.
10. Generates visual outputs and reports.

---

## Key Features

### 🛰️ Satellite Image Road Extraction

ATLAS uses a two-model segmentation ensemble:

- **D-LinkNet34**
- **RoadGIE**

The production ensemble combines their probability maps using:

```text
D-LinkNet34 weight = 0.65
RoadGIE weight     = 0.35
Ensemble threshold = 0.275
The ensemble produces the final binary road mask used by the downstream ATLAS pipeline.

🧩 Road Network Reconstruction

The predicted road mask is transformed into a structural representation of the road network.

The pipeline includes:

Road segmentation
Post-processing
Skeletonization
Graph construction
Node extraction
Edge extraction
Topological analysis

This allows ATLAS to move from pixel-level computer vision to network-level analysis.

🕸️ Topology & Criticality Analysis

The extracted road network is represented as a graph.

ATLAS analyses:

Network nodes
Network edges
Connectivity
Connected components
Largest connected component
Critical nodes
Critical edges
Structural importance

This makes it possible to identify infrastructure whose failure could significantly affect network connectivity.

⚠️ Network Resilience Simulation

ATLAS can simulate infrastructure failures and observe their effect on the road network.

Supported failure scenarios include:

Critical node failure
Selected node failure
Critical edge failure
Selected edge failure

Example workflow:

Original Road Network
        ↓
Identify Critical Element
        ↓
Remove Node / Edge
        ↓
Recalculate Connectivity
        ↓
Measure Network Fragmentation
        ↓
Estimate Resilience Impact

This allows the system to investigate questions such as:

What happens to the road network if an important junction becomes unavailable?

📊 Risk Assessment

ATLAS derives resilience-related metrics from the resulting graph structure.

The system evaluates quantities including:

Connected components
Largest connected component
Network fragmentation
Average Resilience Index (ARI)
Risk classification
Recommendations

The goal is to translate graph-level changes into interpretable infrastructure-risk information.

🗺️ Interactive Geospatial Workstation

The frontend is designed as a geospatial analysis workstation rather than a simple form-based application.

The interface integrates:

Image upload
Segmentation visualization
Layer-based visualization
Analysis inspection
Topology visualization
Criticality visualization
Resilience simulation
Risk assessment
Report generation
📄 Automated Reporting

ATLAS generates visual outputs and reports from the computed analysis results.

The reporting workflow can present:

Input analysis
Segmentation results
Network structure
Critical elements
Resilience metrics
Risk assessment
Simulation results
Recommendations
System Architecture
                         ┌──────────────────────┐
                         │     Satellite Image  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   ATLAS FastAPI API  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                  ┌─────────────────────────────────┐
                  │     Road Segmentation Ensemble  │
                  │                                 │
                  │  D-LinkNet34 ──────── 0.65      │
                  │  RoadGIE ──────────── 0.35      │
                  │                                 │
                  │  Threshold = 0.275             │
                  └───────────────┬─────────────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │     Road Mask       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Skeletonization    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    Road Graph       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Topology Analysis  │
                       └──────────┬──────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              Criticality     Resilience      Risk
                    │             │             │
                    └─────────────┼─────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Failure Simulation  │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Visualization &     │
                       │ Reporting           │
                       └─────────────────────┘
Machine Learning Pipeline

ATLAS uses an ensemble-based road extraction approach.

Input Satellite Image
        │
        ├────────────────┐
        ▼                ▼
  D-LinkNet34         RoadGIE
        │                │
        ▼                ▼
 Probability Map    Probability Map
        │                │
        └────────┬───────┘
                 ▼
        Weighted Ensemble
                 │
        0.65 × D-LinkNet34
        0.35 × RoadGIE
                 │
                 ▼
        Threshold = 0.275
                 │
                 ▼
          Binary Road Mask

The ensemble combines the probability outputs of the two segmentation models before applying the final threshold.

Graph & Resilience Pipeline

Once the road mask is generated, ATLAS moves from computer vision into network analysis.

Binary Road Mask
       ↓
Skeleton
       ↓
Graph Construction
       ↓
Nodes + Edges
       ↓
Topology Analysis
       ↓
Criticality Detection
       ↓
Failure Simulation
       ↓
Connectivity Analysis
       ↓
Resilience / Risk Assessment

This connects image-level perception with graph-level reasoning.

Example Analysis

A typical ATLAS analysis can produce information such as:

Road Network
├── Number of nodes
├── Number of edges
├── Critical node
├── Critical edges
├── Connected components
├── Largest connected component
├── Resilience metrics
├── Risk classification
└── Failure simulation results

For example, a critical-node failure can remove an important junction and recompute the resulting network connectivity.

This allows ATLAS to investigate:

How vulnerable is the extracted road network to the failure of an important infrastructure component?

Technology Stack
Frontend
React
TypeScript
Vite
Tailwind CSS
Framer Motion
Lucide
Recharts
React Query
Axios
Backend
Python
FastAPI
Uvicorn
Pydantic
Machine Learning
PyTorch
Torchvision
Segmentation Models PyTorch
timm
Transformers
OpenCV
Pillow
NumPy
SciPy
scikit-image
Geospatial & Graph Processing
Rasterio
NetworkX
Affine
OpenCV
NumPy
Visualization & Reporting
Matplotlib
ReportLab
Development & Reproducibility
Docker
Docker Compose
Git
Git LFS
Project Structure
atlas/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── engines/
│   │   └── main.py
│   │
│   ├── models/
│   │   └── dlinknet/
│   │
│   ├── outputs/
│   ├── requirements-full.txt
│   └── requirements-render.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   └── api/
│   └── package.json
│
├── RoadGIE/
│   └── checkpoint/
│
├── docker/
│   └── Dockerfile
│
├── .gitattributes
├── .gitignore
└── README.md
Running ATLAS Locally
Prerequisites

Install:

Python 3.12+
Node.js
npm
Git
Git LFS
Docker Desktop (optional)
1. Clone the Repository
git clone https://github.com/DeepikaReddy0607/atlas.git
cd atlas

Initialize Git LFS:

git lfs install
git lfs pull
2. Backend Setup

Navigate to the backend:

cd backend

Create a virtual environment:

python -m venv venv

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements-full.txt

Start the FastAPI server:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Health check:

http://127.0.0.1:8000/health

Interactive API documentation:

http://127.0.0.1:8000/docs
3. Frontend Setup

Open another terminal:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Open the Vite URL displayed in the terminal.

4. Docker

ATLAS includes a Dockerized backend for reproducible execution.

Build the backend image:

docker build -f docker/Dockerfile -t atlas .

Run the container:

docker run -p 8000:8000 atlas

Health check:

http://localhost:8000/health

The Dockerized backend has been tested locally through the complete inference pipeline, including:

Model loading
File upload
D-LinkNet34 inference
RoadGIE inference
Ensemble inference
Output generation
Model Weights

The production model weights are managed using Git LFS because of their size.

The production ensemble consists of:

D-LinkNet34
RoadGIE

Pull the model files after cloning:

git lfs install
git lfs pull
Production Ensemble

The final ATLAS road-extraction configuration is:

Component	Configuration
Model 1	D-LinkNet34
Model 2	RoadGIE
D-LinkNet34 Weight	0.65
RoadGIE Weight	0.35
Ensemble Threshold	0.275
Inference Device	CPU

The ensemble produces the road probability map used by the downstream topology and resilience pipeline.

Engineering Highlights

ATLAS was developed as a complete software and machine-learning system rather than as an isolated model experiment.

Major engineering areas include:

Deep-learning segmentation
Ensemble inference
Image preprocessing
Geospatial processing
Skeletonization
Graph construction
Network topology analysis
Critical infrastructure identification
Failure simulation
Resilience analysis
Risk classification
REST API development
Interactive React application development
Dockerization
Git LFS model management
Automated visualization
Report generation
Design Philosophy

The central idea behind ATLAS is to bridge the gap between AI perception and decision-oriented network analysis.

A segmentation model can answer:

Where are the roads?

ATLAS continues further:

How are those roads connected?

Which parts of the network are structurally important?

What happens if an important component fails?

How severely does the network fragment?

The system therefore combines computer vision with graph theory to move from road detection toward road-network understanding.

Current Status
Completed
 React + TypeScript frontend
 FastAPI backend
 Satellite image upload
 D-LinkNet34 inference
 RoadGIE inference
 Weighted segmentation ensemble
 Road skeletonization
 Graph construction
 Topology analysis
 Criticality analysis
 Node failure simulation
 Edge failure simulation
 Resilience analysis
 Risk assessment
 Interactive visualization
 Report generation
 Dockerized backend
 Git LFS model management
 End-to-end local testing
Limitations

ATLAS is currently intended as a research, demonstration, and portfolio system rather than a production emergency-management platform.

Important limitations include:

Model performance depends on the characteristics of the input imagery.
Segmentation errors can propagate into the graph representation.
Graph reconstruction quality depends on the quality of segmentation and skeletonization.
Simulation results represent the modeled road network and do not directly model real-world infrastructure behaviour.
The current system is primarily designed for local and reproducible execution.
Future Directions

Potential extensions include:

Larger-scale geospatial datasets
Multi-region evaluation
Temporal road-network monitoring
Improved geospatial coordinate handling
More detailed accessibility modelling
Multi-hazard simulation
Real-world GIS integration
Cloud-scale inference
Model optimization for edge deployment
Why ATLAS?

Traditional road-segmentation systems primarily focus on identifying road pixels in imagery.

ATLAS attempts to take the analysis one step further.

Satellite Imagery
       ↓
"What roads exist?"
       ↓
Road Segmentation
       ↓
"How are they connected?"
       ↓
Graph Construction
       ↓
"Which components matter most?"
       ↓
Criticality Analysis
       ↓
"What if one fails?"
       ↓
Failure Simulation
       ↓
"How much does the network degrade?"
       ↓
Resilience & Risk Analysis

This creates a unified workflow connecting:

Computer Vision + Geospatial Processing + Graph Theory + Network Resilience

Project Goal

ATLAS explores how satellite imagery, deep learning, graph theory, and resilience analysis can be combined into a single decision-support workflow for understanding road infrastructure.

The project focuses on moving beyond:

"Detect the roads."

toward:

"Understand the network and its vulnerability."

Author

Deepika Reddy

Built as an end-to-end machine-learning, geospatial analysis, and software engineering project.
```