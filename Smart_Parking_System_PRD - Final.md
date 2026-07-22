# Product Requirements Document (PRD)
## Smart Parking System Using Computer Vision and Artificial Intelligence

---

## 1. Project Overview

**Brief Description**
The Smart Parking System is a computer vision prototype designed to monitor parking slot occupancy in real time using video feeds (simulated via webcam for this phase). By processing live footage through a custom YOLOv8 model, the system tracks vehicle presence and updates a web UI using intuitive color indicators: Green for available and Red for occupied.

**Purpose**
Finding a parking spot on campus is currently an unmonitored process with high operational waste. From an Industrial Engineering perspective, this project treats parking search as a system bottleneck that generates non-value-added time, excess fuel consumption, and unnecessary traffic motion. The objective is to replace random search behavior with real-time visibility.

---

## 2. Problem Statement

**Current Problem**
A preliminary survey of 13 students conducted for this project shows that searching for parking during peak hours (8:00 AM–12:00 PM) is a significant and recurring issue:
- Search Time: 85% of students spend more than 5 minutes looking for parking, with a significant portion requiring 11–20 minutes.
- Punctuality Impact: 85% have missed or arrived late to lectures/exams due to parking congestion (62% experienced this 4 times this semester).
- Walking Distance: 92% are forced to park over 200 meters from their destination, and 31% walk more than 500 meters (7+ minutes on foot).

Because there is no visibility into which spots are free, students rely on inefficient coping behaviors: **77%** drive directly to distant/unpaved overflow lots, **46%** wait inside their car hoping a spot opens up, and **38%** resort to incorrect or double-parking when in a hurry.

- **A preliminary survey of 13 students was conducted to better understand the parking challenges during peak hours. The findings presented below are based on the responses collected from this survey.

**Impact on Students**
- Lost time before classes, which may accumulate over the course of a semester.
- Increased stress and higher likelihood of arriving late to lectures and exams.
- Unnecessary walking distances and physical inconvenience.

**Impact on University Operations**
- Unstructured vehicle circulation may contribute to traffic congestion and unnecessary fuel consumption.
- Duble-parking and improper parking can reduce usable capacity and create safety hazards.
- Parking demand and utilization are currently invisible to facilities management, making it impossible to plan capacity or measure performance.
- Encouragingly, 85% of surveyed students said they would use a real-time parking app if available, and 54% said they would redirect to a farther-but-open parking lot if informed in advance. These findings suggest that students are receptive to a real-time parking guidance solution.

---

## 3. Objectives

### Business & Operational Goals
* **Reduce Lateness:** Minimize time spent hunting for spots to help students arrive on time.
* **Campus Visibility:** Provide facilities management with clear data on parking slot occupancy.
* **Asset Optimization:** Reuse existing CCTV camera infrastructure to eliminate hardware costs.

### Technical & Engineering Goals
* **Real-time Detection:** Process video streams instantly using YOLOv8 to update slot availability (Green = Open, Red = Occupied).
* **Eliminate Waste:** Direct drivers straight to open spots, reducing unnecessary vehicle movement ("motion waste").
* **Scalable Architecture:** Build a modular system that can easily extend to additional camera angles and zones.

---

## 4. Proposed Solution

.The proposed system is designed to use existing CCTV cameras positioned over parking zones to continuously capture video. In the current prototype, a webcam is used to simulate the CCTV video feed. A computer vision model (YOLOv8) is used to process each frame, detect vehicles, and determine whether each mapped parking slot is occupied or available. The parking status is then displayed through a simple web interface using green (available) and red (occupied) indicators. By reusing existing camera infrastructure in a real deployment, the solution aims to minimize implementation cost and installation effort.

---

## 5. Target Users

- **Primary users:** University students who commute by car and need to find parking during peak hours.
- **Secondary users:** University facilities/operations staff, who benefit from occupancy data for planning and reporting.
- **Indirect stakeholders:** Faculty and staff affected by traffic congestion and late-arriving students.

---

## 6. User Journey

1. A student is preparing to leave for the university and opens the parking app.
2. The app displays the current status of each parking zone using green/red indicators.
3. The student identifies an available zone and decides on a route accordingly, or is informed that the nearest lot is full and a specific alternate lot is open.
4. The student drives directly to the identified available slot, without circling the lot searching.
5. Upon arrival, the student parks in the confirmed available spot.
6. The system updates the slot status to "Occupied" as soon as the vehicle is detected, reflecting the new state for the next user.

- **The following scenario represents the expected user journey for the proposed system if deployed in a real-world environmen
---

## 7. Expected Success Metrics (Projected KPIs)

| The following KPIs represent projected targets for evaluating the proposed system if it is deployed in a real campus environment. They are expected outcomes and not results measured from the prototype.
| KPI | Description | Target |
|---|---|---|
| Average parking search time | Expected average time required to find a parking space | Reduce by ≥ 50% |
| Lecture/exam lateness incidents | Expected reduction in students arriving late due to parking search | Reduce by ≥ 50% |
| App adoption rate | Expected percentage of students who would use the system | ≥ 70% |
| Reduction in improper/double-parking incidents | Expected reduction in improper or double-parking incidents | Reduce by ≥ 30% |

## 8. Future Roadmap (Out of Scope)

* **Extended Coverage:** Expand camera detection to overflow and unpaved campus lots.
* **Predictive Analytics:** Estimate slot availability based on time-of-day and class schedules.
* **Campus Navigation:** Integrate turn-by-turn directions directly to the assigned slot.
* **Smart Alerts:** Send push notifications for open spots 15 minutes before class time.
* **Analytics Dashboard:** Provide campus facilities with historical utilization heatmaps.