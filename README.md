# Robots4ChildrenWithDisabilities
![alt text](assets/robots.png)
Robots4ChildrenWithDisabilities is a summer consulting project exploring how robotics can support and empower children with disabilities. 

## Overview
- Group Information
- Project Information
- Version Control
- Repository Structure
- Extension work

## Group Information
Our team consisted of:
- Adeola Olawoye
- Nicholas Ow
- Isobel Owens
- Dinushan Edmond Camilus
- Gwendal Casta
- Jinyoung Kim
<br>

## Project Information
The project aim was to develop an affordable autonomous robotic assistant capable of playing games and assisting in activities of daily living (ADLs) for children affected by motor disabilities. Designed with the end user in mind, the robot was intended to be friendly, safe, and intuitive to interact with.

To enable user interaction, we implemented accessible input methods such as adaptive game controllers and head tracking systems. We further enhanced the robot’s autonomy by integrating computer vision and imitation learning, allowing it to perceive, adapt, and respond intelligently to its environment.

From a technical perspective, the system combined a modular hardware architecture with a ROS-based software framework, supporting real-time control and sensor integration. The vision module utilized object detection and facial tracking to enable dynamic interaction, while the learning algorithms were trained to replicate demonstrated behaviors such as picking and placing objects. This configuration provided a robust and flexible platform for further expansion into assistive and educational robotics applications.

### Project Goals

- Investigate the potential of robotics to enhance accessibility and inclusion for children with physical, cognitive, or developmental disabilities. (I'm not sure for whom the robots are designed)
- Propose actionable, user-centered robotic solutions tailored to the needs of children with disabilities.
- Develop proof-of-concept ideas or prototypes to demonstrate feasibility and impact.

## Version Control

To ensure that a functional version of the robotic assistant would be delivered by the project deadline, we adopted an iterative development workflow. With each iteration, we incrementally increased the system’s autonomy, capability, and user engagement.

The first iteration focused on enabling basic control of the robot through low-dimensional input methods, such as four-directional commands, allowing users to move the robot safely and effectively.

In the next stage, we concentrated on automating the robotic arm module, enabling it to perform pick-and-place operations. Alongside this, we integrated a computer vision module into the navigation system, allowing the robot to detect objects within its environment and approach them autonomously using its mobile base.

Subsequent iterations prioritized user–robot interaction. We developed a child-friendly graphical interface and designed interactive games that leveraged the robot’s existing hardware modules.

Finally, we integrated the system with a LiDAR-based mapping framework to enhance navigational flexibility and spatial awareness. Additional features, such as user-to-user messaging and improved robot dialogue responses, were implemented to increase communication capabilities and create a more engaging, friendly user experience.

## Repository Structure

- `GUI/`: Contains code for motion control, user–robot interaction interfaces, task sequencing logic, and system integration.
- `ROS2/`:ROS 2 packages and scripts responsible for LiDAR-based mapping, navigation, and environment perception..
- `3D Print/`: CAD and STL files for the robot’s 3D-printed mechanical components and structural parts.
