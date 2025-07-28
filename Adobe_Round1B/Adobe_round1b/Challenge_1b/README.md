# Challenge 1b: Multi-Collection PDF Analysis

## Overview

This project provides a fully optimized solution to **Challenge 1B**, where the task is to extract and rank the most relevant **sections** and **subsections** across 3–10 PDFs per collection, tailored to a defined **persona** and **job-to-be-done**.
The system runs **offline**, uses a **≤1GB model**, executes **under 60 seconds** (for up to 5 collections), and outputs a structured JSON format with **high accuracy**.

## Project Structure
```
Challenge_1b/
├── input/
│ ├── Collection 1/
│ │ ├── PDFs/
│ │ └── challenge1b_input.json
│ ├── Collection 2/
│ ├── Collection 3/
│ ├── Collection 4/
│ └── Collection 5/
├── output/
│ ├── Collection_1_output.json
│ ├── Collection_2_output.json
│ ├── Collection_3_output.json
│ ├── Collection_4_output.json
│ └── Collection_5_output.json
├── main.py
├── pdf_analyzer.py
├── Dockerfile
├── requirements.txt
├── README.md
├── approach_explanation.md
└── challenge1b.log
```

## Collections

### Collection 1: Travel Planning
- **Challenge ID**: round_1b_002
- **Persona**: Travel Planner
- **Task**: Plan a 4-day trip for 10 college friends to South of France
- **Documents**: 7 travel guides

### Collection 2: Adobe Acrobat Learning
- **Challenge ID**: round_1b_003
- **Persona**: HR Professional
- **Task**: Create and manage fillable forms for onboarding and compliance
- **Documents**: 9 Acrobat guides

### Collection 3: Recipe Collection
- **Challenge ID**: round_1b_001
- **Persona**: Food Contractor
- **Task**: Prepare vegetarian buffet-style dinner menu for corporate gathering
- **Documents**: 9 cooking guides

## Input/Output Format

### Input JSON Structure
Each collection directory should include a `challenge1b_input.json`:
```json
{
  "challenge_info": {
    "challenge_id": "round_1b_001",
    "test_case_name": "travel_test_case"
  },
  "documents": [
    { "filename": "guide1.pdf", "title": "France Guide" }
  ],
  "persona": { "role": "Travel Planner" },
  "job_to_be_done": { "task": "Plan a sustainable trip" }
}
```

### Output JSON Structure
Each run generates a Collection X_output.json per input collection the output will be in the below format 
```json
{
  "metadata": {
    "input_documents": [
      "South of France - Cities.pdf",
      "South of France - Cuisine.pdf",
      "South of France - History.pdf",
    ],
    "persona": "Travel Planner",
    "job_to_be_done": "Plan a trip of 4 days for a group of 10 college friends.",
    "processing_timestamp": "2025-07-27T12:30:07.586169",
    "processing_time_seconds": 33.48
  },
  "sections": [
    {
      "document": "South of France - Tips and Tricks.pdf",
      "page_number": 8,
      "section_title": "Tips and Tricks for Packing",
      "importance_rank": 1
    },
    {
      "document": "South of France - Things to Do.pdf",
      "page_number": 2,
      "section_title": "Water Sports",
      "importance_rank": 2
    },
  ],
  "subsection_analysis": [
    {
      "document": "South of France - Tips and Tricks.pdf",
      "refined_text": "• Check the Weather: Check the forecast before packing to ensure appropriate clothing. • Make a Packing List: Create a list to ensure nothing is forgotten. Cross oﬀ items as you pack. • Use Packing Cubes: Organize clothes and maximize space. • Roll Your Clothes: Save space and reduce wrinkles. • Pack Dual-Purpose Items: Choose items that serve multiple purposes. • Wear Bulky Items: Wear bulky items like coats or boots during travel to save suitcase space. • Pack a Day Bag: Bring a small day bag for daily excursions. • Leave Room for Souvenirs: Leave extra space or bring a foldable bag for souvenirs. • Additional Tips: Pack a small travel umbrella, a reusable shopping bag, and a portable phone charger. Consider using a luggage scale to avoid overweight baggage fees.",
      "page_number": 8
    },
    {
      "document": "South of France - Tips and Tricks.pdf",
      "refined_text": "• Electronics: Smartphone, charger, power bank, and other devices. Bring a travel adapter if needed. • Camera: Capture memories with a camera, extra batteries, and memory cards. • Books and Entertainment: A book, e-reader, or tablet for entertainment during travel. • Additional Tips: Download maps and travel guides to your devices for oﬄine use. Consider bringing a portable Wi-Fi hotspot for reliable internet access.",
      "page_number": 4
    },
    {
      "document": "South of France - Tips and Tricks.pdf",
      "refined_text": "• Day Bag: A small, secure day bag for carrying essentials like water, snacks, and a camera. • Comfortable Shoes: Wear comfortable walking shoes for exploring cities. • Guidebook: A guidebook or map to help navigate and find points of interest. • Additional Tips: Use a money belt or hidden pouch to keep valuables safe. Consider using public transportation to explore cities eﬃciently.",
      "page_number": 7
    },
    {
      "document": "South of France - Tips and Tricks.pdf",
      "refined_text": "Packing for a trip to the South of France involves considering the season, planned activities, and the needs of both adults and children. By following this comprehensive guide and incorporating the tips and tricks provided, you'll be well-prepared for a comfortable and enjoyable trip. Remember to pack light, versatile clothing, and essential items to make the most of your travel experience. Bon voyage!",
      "page_number": 9
    },
    {
      "document": "South of France - Tips and Tricks.pdf",
      "refined_text": "• Diapers and Wipes: For babies or toddlers, pack enough diapers and wipes. • Snacks: Bring a variety of snacks for travel and outings. • Toys and Entertainment: Favorite toys, books, or games. Consider a tablet with predownloaded content. • Additional Tips: Pack a small backpack for each child with their essentials to keep them engaged. Include comfort items like a favorite blanket or stuﬀed animal.",
      "page_number": 6
    }
  ]
}
```

## Key Features
Persona- and job-specific content analysis

Section scoring with relevance and diversity penalties
 
Subsection ranking with deduplication

Batch embedding and fallback for flat PDFs

Optimized threading and multiprocessing

Fully offline (model preloaded in Docker)

Output matches strict Challenge 1B format

---


Docker Instructions
  Build the Image
docker build -t challenge1b-solution .

Run the Analyzer
docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" challenge1b-solution python main.py
or
docker run -v "${PWD}:/app" challenge1b-solution python main.py 

**Note**: This README provides a brief overview of the Challenge 1b solution structure based on available sample data. 