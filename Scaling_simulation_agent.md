**Scaling simulation agent**

**Concern:**  
Here we have a list of simulations [https://github.com/ANURAGMN/SimulationsNCERT](https://github.com/ANURAGMN/SimulationsNCERT). 

1. Just observing and changing the parameters on their own, the simulation needn’t help student learn the key aspects of the simulations.   
2. Also, students can be of different calibre( Dull, Medium, High IQ)  with different stages of learning (Beginners, Intermediate, Advanced).

**Solve:**   
To design the simulation agent such that it’ll be able to intake any simulations (mostly in html) and then walk students through helping them understand the key elements from the simulation.   
**For ex:**  
*If you observe the foundational tsd html or acids and bases, they are good simulations, but the problem is that without previous knowledge, it’s very difficult to make it understandable for students the key concepts.*   
So we need to Build an adaptive, scalable AI agent that:

* *Ingests any HTML-based science simulation*  
* *Identifies and teaches 3–4 key intuitions/concepts at every level*  
* *Adjusts depth and guidance based on the learner’s level*  
* *Interacts conversationally to engage the learner*  
* *Tests conceptual understanding via short MCQs*

**Approach:**

* Derive the 3-4 key concepts or intuitions that the student needs to build. Specify the parameters that need to be set.   
* Go with the simulation agent. Here simulation agent needs to be scalable in the sense that, irrespective of the simulation in discussion, it needs to be able to bring the intuitions alive conversationally.

* **Inputs:**   
  a) Simulation html link,   
  b) Description of the simulation   
  c) Parameters in consideration   
  d) Description of the NCERT chapter broken down (Refer: [https://github.com/ANURAGMN/NCERT\_Textbook\_Breakdown](https://github.com/ANURAGMN/NCERT_Textbook_Breakdown) )  
    
* **Output needs to contain:**   
    
  a) **Upto 3 key takeaways for every stage of learning (Beginners, Intermediate, Advanced)**:  
  3 key takeaways for Beginner can involve basic definition/ basic equation with a very simple change that needs to be done for  1-2 parameter. For ex: for acids/bases, Definition of acids, Bases and ph paper with changing ph parameter can be 1-2 takeaways. Similarly for Medium: It can involve varying the Reasoning behind the change in color/ examples for acids and bases and when discovering the changes when clicked on the examples. For Advanced, Addition and subtraction of elements and their change in the ph value.  
  **Note**: *The selection of the level should be made selectable for the students.*    
    
  b) **Parameters to be changed to establish the key takeaways**:   
  For every key takeaway (loop through them one after the other upto 3 key takeaways within the level), there needs to be specific parameters that need to be varied. For ex: for the Addition and subtraction of elements and their change in the pH value, the parameters that need to be changed are adding/subtracting the acids/bases, thereby changing the ph of the solution.   
    
  c) **Identifier like Before/After or None:**   
  It’s helpful for the students to identify the difference because of the changes in the values in the parameters. For ex: In the case of a pendulum, if the length parameter is varied from 2 m to 10 m, it’s important to show both these simulations side by side for effective understanding   
    
  **d) MCQs to test the key takeaways they learnt**  
    
  **e) Interactive agentic flow:**   
  The flow should have the interactivity driven by Agentic implementation.    
  **Probable agentic nodes**:   
  1\. Greet the user and brief what the simulation is about   
  2\. Display the Simulation and ask students to change 1-2 parameters and check.   
  3\. Note the changes done and ask the students what they discovered when they changed the parameters.  
  4\. Depending upon their level, take them through the Key takeaways. If the identifier is before/after then display the simulation side by side (on streamlit) or else, a single display.   
  5\. After every display, agent needs to probe the student to know what they discovered or learnt  
  6\. Auto-suggested node (Human in the loop) whether they would like to cover the next level if exists or goto the MCQ to test what they learn basis the interaction.   
    
  **Note**: *Some of the constraints can be a) Upto 2 interactions within a node b) LLM text output to have less than 100 words c) No bold statements*  
  


**What we had tried before which needs complete revamp:** 

* CC node that brings 3-4 key elements. Then GE node loop. Then sim vars, then sim execute. Following the flow defined here [https://docs.google.com/document/d/1KKhEtJS0mP5-ISkhE-nkvTchunS4EqunZwDdp7SVmoM/edit?usp=sharing](https://docs.google.com/document/d/1KKhEtJS0mP5-ISkhE-nkvTchunS4EqunZwDdp7SVmoM/edit?usp=sharing)  
  


**For the demo**: 1\. Let’s have this on VS or Colab. 2\. Later, try hosting on Streamlit 3\. Thereafter, as a standalone Api on EC2 or any cloud services. 

**Ref:**   
**1\. [https://github.com/ANURAGMN/SimulationsNCERT](https://github.com/ANURAGMN/SimulationsNCERT)**  
**2\. [https://github.com/ANURAGMN/NCERT\_Textbook\_Breakdown](https://github.com/ANURAGMN/NCERT_Textbook_Breakdown)**  
**3\.[https://docs.google.com/document/d/1KKhEtJS0mP5-ISkhE-nkvTchunS4EqunZwDdp7SVmoM/edit?usp=sharing](https://docs.google.com/document/d/1KKhEtJS0mP5-ISkhE-nkvTchunS4EqunZwDdp7SVmoM/edit?usp=sharing)**  
**4\. [https://chatgpt.com/share/68c6b886-6c88-8007-9209-add5ac23fab5](https://chatgpt.com/share/68c6b886-6c88-8007-9209-add5ac23fab5)**  
**5\. [https://chatgpt.com/share/68c6b886-6c88-8007-9209-add5ac23fab5](https://chatgpt.com/share/68c6b886-6c88-8007-9209-add5ac23fab5)**

