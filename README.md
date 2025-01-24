---

# MEDISCANAI: Breast Ultrasound Imaging Annotation Tool

## Project Overview
MEDISCANAI is a Python-based annotation tool developed to enhance the annotation of breast ultrasound images. The tool integrates the ACR BI-RADS classification system, enabling medical professionals to annotate, categorise, and export ultrasound image data. Designed with medical professionals and AI researchers in mind, the tool facilitates high-quality dataset generation for supervised machine learning applications in breast cancer detection.

This project was developed as part of a dissertation submitted in May 2024 for the BSc Computer Science degree at the University of Derby.

---

## Features

### **Core Functionalities**
- **User Login and Interface Selection**:
  - Supports login for medical professionals and AI researchers.
  - User-specific functionalities tailored to clinical or research workflows.
- **Annotation Tools**:
  - Lesion Pen Tool: Allows precise boundary drawing around lesions.
  - Arrow Tool: Highlights specific areas of interest.
  - Orientation Tool: Measures lesion diameters.
  - Highlight Tool: Identifies BI-RADS-related features (e.g., echo pattern, margins).
  - Calcification Tool: Pinpoints micro- and macro-calcifications.
- **BI-RADS Classification**:
  - Fully integrated BI-RADS form for detailed lesion analysis.
  - Real-time entry validation to ensure data consistency.
- **Image Management**:
  - Save and load annotation data and BI-RADS forms in JSON format.
  - Annotation and image storage using a local, secure JSON-based database.
- **AI Researcher Interface**:
  - Enables dataset viewing and bulk export.
  - Displays detailed annotation summaries for each image.

### **Advanced Capabilities**
- **Custom GUI Design**:
  - Built with Tkinter for an intuitive and user-friendly interface.
  - Dark-themed UI to reduce eye strain during extended usage.
- **Optimised for AI Training**:
  - High-quality, structured datasets suitable for machine learning applications.
  - JSON export format for seamless integration with AI frameworks.

---

## Motivation and Contribution

### **Motivation**
Breast cancer is one of the leading causes of cancer-related mortality. Early detection significantly improves survival rates. Despite advancements in imaging technologies, existing tools for annotating ultrasound images lack the precision and usability required for clinical and research settings. MEDISCANAI aims to bridge this gap by:
- Simplifying the annotation process.
- Ensuring data integrity and consistency.
- Generating high-quality datasets for AI-driven cancer detection.

### **Key Contributions**
1. **Integration of BI-RADS**:
   - Combines medical annotation with BI-RADS reporting for streamlined diagnostics.
2. **Custom Annotation Framework**:
   - Tailored specifically for breast ultrasound imaging.
3. **Dataset Generation for AI**:
   - Simplifies dataset creation for supervised machine learning research.

---

## System Design

### **Folder Structure**
```
MEDISCANAI/
│
├── mediscantai_main.py
├── README.md
├── data/
│ ├── images/
│ ├── annotations/
│ └── logs/
├── resources/
│ ├── BI-RADS_guide.pdf
│ ├── logo/
│ └── screenshots/
├── tests/
├── user_docs/
│ └── UserGuide.pdf
└── requirements.txt
```

### **Workflow**
1. User logs in and selects their role (Doctor or AI Researcher).
2. Medical professionals annotate images using the provided tools.
3. Annotations are saved alongside BI-RADS classifications in JSON format.
4. AI researchers access and export annotations for dataset generation.

---

## Prerequisites

### **Hardware and OS Requirements**
- OS: Windows 10/11 or Linux (Ubuntu 20.04+ recommended).
- RAM: Minimum 4GB (8GB recommended).
- CPU: Intel Core i5 or equivalent.

### **Software Requirements**
- **Python 3.9+**
- **Dependencies**:
  - Tkinter
  - NumPy
  - Matplotlib
  - Pillow (PIL)

---

## Usage Instructions

### **Running the Application**
1. Navigate to the project directory:
   ```bash
   cd MEDISCANAI/
   ```
2. Launch the application:
   ```bash
   python annotation_tool_load.py
   ```

### **Annotation Workflow**
- **Step 1**: Upload an ultrasound image.
- **Step 2**: Use annotation tools to identify lesions and key features.
- **Step 3**: Complete the BI-RADS form for the identified lesions.
- **Step 4**: Save annotations and export data as needed.

---

## Testing and Evaluation

- **Usage Scenarios**:
  - Malignant and benign lesion annotation with BI-RADS reporting.
  - Dataset export and quality validation for AI researchers.
- **Performance Metrics**:
  - Annotation accuracy.
  - User satisfaction (based on feedback from medical professionals and researchers).

---

## Screenshots
![image](https://github.com/user-attachments/assets/78f6ca03-81fc-4f27-84f3-7bf380265eb4)

![image](https://github.com/user-attachments/assets/ce624c53-3d3d-4f70-9285-6e9b8f824f91)

![image](https://github.com/user-attachments/assets/f2cc0ffe-16a8-4d40-b604-234005a177ea)

![image](https://github.com/user-attachments/assets/62c15691-f8ed-484f-8667-8811a32ab486)

![image](https://github.com/user-attachments/assets/1aca612d-12b8-4597-8e69-2846e651f43e)

![image](https://github.com/user-attachments/assets/df269d9c-cece-4ca0-98aa-c360ce43f658)

![image](https://github.com/user-attachments/assets/fd7fac9b-0379-4e1a-b57b-d2efc18f7b5c)

![image](https://github.com/user-attachments/assets/c418ab89-1d14-4547-beda-0ad297a2bd08)

![image](https://github.com/user-attachments/assets/81cc2388-2d27-4f50-af77-9023aacd567d)

![image](https://github.com/user-attachments/assets/70061e65-b6da-4f28-9d45-b6e7c428aac8)

![image](https://github.com/user-attachments/assets/3c84d5ea-fb2c-4150-a2f6-c8c415bdf304)

![image](https://github.com/user-attachments/assets/ef42c2c1-0050-4670-adea-5030debf01a0)

![image](https://github.com/user-attachments/assets/126e4d0b-b3f3-4794-aac9-9a4b5c6a458c)

---

## Future Enhancements

1. **Automated Annotation Assistance**:
   - AI-driven suggestions for lesion boundaries and BI-RADS classification.
2. **Expanded Modalities**:
   - Support for other medical imaging formats (e.g., mammograms, CT scans).
3. **Cloud Integration**:
   - Enable secure remote storage and collaboration features.

---

## Acknowledgments

I would like to extend my deepest gratitude to:
- **Dr. Alaa AlZoubi**: For their guidance and invaluable insights throughout the project.
- **Dongxu Han and Hongbo Du**: For their constructive feedback and encouragement.
- **Family and friends**: For their unwavering support and motivation.

---
