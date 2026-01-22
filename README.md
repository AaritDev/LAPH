![banner](laph.png?raw=true)
# Local Autonomous Programming Helper

## 🧠 What L.A.P.H. Actually Is (Full Corporate Jargon Mode):
An offline, multi-agent coding system that writes, runs, debugs, and fixes its own code using self-reflection and error-aware model routing.

## 🍼 What That Means in Human Words:
A lil AI homie who writes code, runs it, sees if it exploded, learns from the explosion, and tries again.
(Linux-only for now — because Arch btw.)

## 🚀 Vision
L.A.P.H. is designed as a fully offline, privacy-preserving, developer-grade AI agent that:
1. Writes code
2. Runs code
3. Reads the errors
4. Fixes itself
5. …and keeps iterating until the output is clean.
Think of it as your local junior developer intern that never complains, never sleeps, and runs entirely on your machine. No API keys. No cloud. No telemetry. Just vibes and compute.

## 🎯 Project Roadmap
 - Phase 1 — Core Autonomy (MVP):
   Generate → run → capture error → fix → repeat
   Local LLM loop via Ollama/Qwen3
   Basic sandboxing
   Minimal project memory (state.txt and error logs)
   Status: In development (started 17 Nov 2025)

 - Phase 2 — Vision Feedback Loop:
   Screenshot-based error analysis
   GUI inspection using a tiny local vision model
   Model learns from both text errors and visual glitches
   Self-correction for tkinter/PyQt/pygame apps

 - Phase 3 — Multi-Model Pipeline + Agentic Skills:
   “Thinker model” (e.g., Qwen3-14B)
   “Coder model” (e.g., smaller 3B/4B model)
   “Vision model” (qwen3-vl:8b)
   Dynamic routing based on task complexity
   Auto-install missing libraries
   Auto-optimize its own parameters
   Generates a persistent activity log via a super-tiny 1B summarizer

## ⚡ Quickstart:
Install prerquisites:
 1. Python 3.11
 2. The latest ollama version installed
 3. Internet (required **only** for initial model download and setup)

### Also these are the requirements:
 1. at least a 6GB VRAM GPU
 2. 16GB RAM
 3. A CPU that won't   bottleneck the GPU, I dont know much about CPUs

Install:
``` sh
chmod +x ./install.sh
./install.sh
```

Configure your model endpoint in:
"core/llm_interface.py"

After everything is done to run the program just search LAPH in your application launcher or application menu,
the program data is all stored in userspace or ~/home/$HOME so not systemwide.

### 📅 Date Started: 17 November 2025

## DISCLAIMER
This project uses AI generated imagery for the logo (./logo.png) and generates code autonomously, the authors are not responsible for generated output
