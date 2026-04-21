class ControlledUnity():

    def __init__(self, kP = 10.0, kI = 0.0001, kD = 0.01):
        self.previous = []
        self.Valve = 0
        self.kP = kP
        self.kI = kI
        self.kD = kD
        self.error_accu = []
    
    def PID(self, input_val, Man_auto = False, SetpointMan = 0.0, SetpointAuto = 0.0):
        """
        Calculates the output of a PID controller (Proportional, Integral, Derivative).

                Args:
                    Man_Auto (bool): Manual mode (True) or automatic mode (False).
                            SetpointMan (bool): Ignored if Man_Auto is True. Manual setpoint mode (True) or automatic mode (False).
                            SetpointAuto (float): The value of the setpoint in automatic mode.

                 Returns:
                     None

                 The method calculates the PID controller output using the current value (input_val) and the setpoint (SetpointAuto).
                 Speed history is stored in self.previous and limited to 100 items.
                 The controller components P, I, and D are calculated and summed to give the output.
                 Output is limited to the range 0-100.
        
        """
        if Man_auto == False:
            # If the PID is in automatic mode...

            # Store the speed vector in a list of 100 elements.
            self.previous.append(input_val)
            if len(self.previous) > 100:
                self.previous = self.previous[-100:]

            SP = SetpointAuto
            E = SP - input_val
            self.error = E

            # Error is the difference between what i have, and my current setpoint. Used the list for that.
            E_accu = [(SP -  elem) for elem in self.previous[-20:]]
            self.error_accu = E_accu
            
            # The proportional action is the error multiplied by a constant.
            aP = self.error * self.kP

            # The integral action is the area of values, divided by the constant.
            aI = (self.kP * (sum(self.error_accu) / (len(self.error_accu)*0.002) * self.kI))

            # The derivative action is the projection to the future (slope) of the error, multiplied by a constant.
            if len(self.previous)>2:
                aD = (self.error_accu[-1]-self.error_accu[-2])*self.kD*self.kP
            else:
                aD = 0.0

            # Add the components of the Proportional, Integral, and Derivative shares.
            Output = self.Valve + aP + aI + aD

            # Limited the output of the valve
            if Output < 0:
                self.Valve = 0
            elif Output > 100:
                self.Valve = 100
            else:
                self.Valve = Output
        
        else:
            # if we are in "Manual" mode, the valve is placed in the position we defined at the setpoint.
            self.Valve = SetpointMan