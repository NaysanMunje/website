---
title: QDD Actuator
subtitle: 3D printed quasi direct drive actuator
preview: A nearly fully 3D printed quasi direct drive actuator with a hand wound BLDC motor and a 6:1 eccentric cycloidal planetary reduction.
date: 2026
github: https://github.com/NaysanMunje/3D-printed-QDD-actuator
thumbnail: _docx_media/image12.png
order: 0
---

This is a quasi direct drive actuator I designed. I've designed gearboxes before, but this time I took it a step further and made the motor as well. Quasi direct drive actuators combine a BLDC motor and a gear reduction into one component, making them very compact and useful for robots (like MIT's Mini Cheetah). My design is nearly fully 3D printed and uses a 6:1 eccentric cycloidal planetary gear reduction. The CAD and bill of materials are on [GitHub](https://github.com/NaysanMunje/3D-printed-QDD-actuator).

![Finished QDD actuator](_docx_media/image12.png)

## Results

- Configuration: 36N42P
- Mass: 468 g
- Width: 40 mm (65 mm with the motor driver)
- Diameter: 106 mm
- Cost: $216 CAD
- Torque: TBD

## How QDD actuators work

There are two components to a QDD actuator, the BLDC motor and the gear reduction. A BLDC motor uses coils of copper wire to induce magnetic fields that spin a rotor with permanent magnets. Inside the coils, a gearbox reduces the rotation of the rotor and gives more torque.

![Exploded view of a QDD motor](_docx_media/image2.png)

[QDD motors for humanoid and quadruped robots](https://www.cubemars.com/qdd-motors-for-humanoid-and-quadruped-robots.html)

## Choosing the gear reduction

I initially wanted to use cycloidal gears like I previously did for my [robotic arm](../cycloidal-gearbox/index.html), but the stator I bought was too small to make that work. I decided to create a planetary gearbox because I had never made one before. I was worried that standard spur gears wouldn't hold up well for a 3D printed design, so I used eccentric cycloidal gears, which I also used in my robotic arm. They provide less backlash and more contact.

I made a simulation to design the gears and exported it as a sketch to Fusion 360. The stator's size still caused some problems, so I could only get a maximum of a 6:1 reduction using a 4 lobed sun gear.

:::gallery _docx_media/image1.png _docx_media/image11.png
:::

## Winding the stator

I had to manually wind the stator using 0.4 mm copper wire, a process that was extremely tedious and I highly recommend against. To wind the stator, I split the 36 teeth into 6 groups of 2, three times for the A, B, and C phases of the motor. The ends of the three wires are soldered together to get a wye connection, which I definitely remember from my electronics classes. It gives more torque than a delta connection. I was able to get 24 turns per tooth.

:::gallery-equal _docx_media/image3.png _docx_media/image10.png
:::

[3D printed QDD robotic actuator (Instructables)](https://www.instructables.com/3D-Printed-QDD-Robotic-Actuator-MIT-Mini-Cheetah-C/)

## Assembly and testing

After winding the stator and gluing magnets to the rotor, the assembly came together easily. The final actuator is about 460 grams and 40 mm wide, with a diameter of around 106 mm. I used an MKS ODrive motor controller with an onboard encoder to get precise angle control.

:::gallery-grid3 _docx_media/image13.png _docx_media/image8.png _docx_media/image11b.png _docx_media/image5.png _docx_media/image9.png _docx_media/image14.png _docx_media/image4.png _docx_media/image15.png _docx_media/image7.png
:::

The power supply I have isn't good enough to properly test torque and rpm, so I'll update this page with those results when I can test the actuator at school. For now, I have done preliminary tests on speed, precision, and general function, all of which I am very happy with.

## Final thoughts

I had a really good time making this. That being said, I am not sure a DIY actuator like this will be a viable solution for my future projects. Considering the cost and the effort it took to make this actuator, I think I may be better off buying machined motors and saving the peace of mind of avoiding winding and magnet gluing errors. Unless I find pre coiled stators and magnet rings for much cheaper, I will likely not be using this actuator design for a major project.
