# Artificial Signal Generator
A Python desktop GUI application built with Tkinter and Matplotlib for generating, visualizing, streaming, and exporting custom mathematical time-domain signals $f(t)$.
## Overview
The Artificial Signal Generator provides a GUI to evaluate user-defined mathematical expressions in real time or over a fixed timeframe. Built on top of NumPy for vector mathematical evaluations and Matplotlib for interactive visual rendering, it allows engineers, researchers, and students to prototype and analyze signal waveforms quickly.
## Features
### Custom Mathematical Formulations: Input custom mathematical functions using $t$ as the time variable. Supports trigonometric, exponential, logarithmic, and basic algebraic operations.
### Dual Execution Modes:
#### Limited Mode: 
Evaluates and plots the complete signal over a specified target duration instantly.
#### Live Mode: 
Continuously streams and updates the waveform using a 5-second sliding window buffer.
### CSV Data Export: 
Export generated time-series data (Time,Signal) to CSV for external post-processing or modeling.Embedded 
### Interactive Canvas: 
High-frequency rendering using Matplotlib's TkAgg backend embedded directly into the Tkinter window hierarchy.
### Automatic Scaling:
Dynamic Y-axis limits that automatically scale around calculated min/max signal amplitudes.
