import torch
from typing import List
import numpy as np
from rlbench.backend.observation import Observation
class LearningAgent():
    """
    General Purpose class to abstract the functionality of the network from the agent.

    Use this as a base class to create differnt Learning Based agenets that can work and be trained on 
    
    different Deep Learning Algorithms. 
    """

    def __init__(self,collect_gradients=False):
        self.learning_rate = None
        self.neural_network = None
        self.optimizer = None
        self.loss_function = None
        self.training_data = None
        self.logger = None
        self.input_state = None
        self.output_action = None
        self.total_train_size = None # This is to mark the size of the training data for the agent. 
        self.collect_gradients = collect_gradients
        self.gradients = {
            'max':[],
            'avg':[],
            'layer':[]
        }
        self.print_every = 40


    def injest_demonstrations(self,demos:List[List[Observation]],**kwargs):
        raise NotImplementedError()

    
    def train_agent(self,epochs:int):
        raise NotImplementedError()
    
    # Keeping it a list of Observation to keep flexibility for LSTM type networks.
    def predict_action(self, demonstration_episode:List[Observation],**kwargs) -> np.array:
        """
        This should Use model.eval() in Pytoch to do prediction for an action
        This is ment for using saved model. This should also ensure returning
        numpy array is of same dimension as ActionMode + 1 (Gripper Open/close)
        """
        raise NotImplementedError()

    def act(self,state:List[Observation],**kwargs):
        """
        This will be used by the RL agents and Learn from feadback from the environment. 
        This will let pytorch hold gradients when running the network. 
        """
        raise NotImplementedError()

    def save_model(self,file_path):
        """
        This will be used to save the model for which ever type of agent(TF/Torch)
        """
        raise NotImplementedError()

    def load_model(self,file_path):
        """
        This will be used to load the model from file.
        """
        raise NotImplementedError()
    

    def load_model_from_object(self,state_dict):
        """
        This will be used to load the model from a dictionary.
        """
        raise NotImplementedError()

class TorchAgent(LearningAgent):

    def __init__(self,collect_gradeints = False):
        super(LearningAgent,self).__init__(collect_gradeints=collect_gradeints)

    def save_model(self,file_path):
        if not self.neural_network:
            return
        self.neural_network.to('cpu')
        torch.save(self.neural_network.state_dict(), file_path)

    def load_model(self,file_path):
        if not self.neural_network:
            return
        # $ this will load a model from file path.
        self.neural_network.load_state_dict(torch.load(file_path))
    

    def load_model_from_object(self,state_dict):
        if not self.neural_network:
            return 
        self.neural_network.load_state_dict(state_dict)
    
    # Expects Named Params from Torch NN Module. 
    def set_gradients(self,named_parameters):
        avg_grads = []
        max_grads= []
        layers = []
        for n, p in named_parameters:
            if(p.requires_grad) and ("bias" not in n):
                layers.append(n)
                avg_grads.append(p.grad.abs().mean())
                max_grads.append(p.grad.abs().max())
        self.gradients['max'].append(max_grads)
        self.gradients['avg'].append(avg_grads)
        self.gradients['layer'].append(layers)
