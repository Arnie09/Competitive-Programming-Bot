
# imports
import os
import sys
import json
import shutil
import subprocess
from time import sleep, time
from datetime import datetime

class Bot:

    def __init__(self):
        print("bot initiated")
        
        
        self.configNames = {
            "javaTemplate", "pythonTemplate", "archivePath", "workingFolderPath"
        }

        self.configData = {}
        self.home = os.getcwd()
        self.messages = [
            "Enter the path of java template",
            "Enter the path of python template",
            "Enter the path of archives folder",
            "Enter the path of the working folder"
        ]

        isConfigComplete = self.checkConfig()

        if (isConfigComplete == False):
            self.runConfig()

        arguments = list(sys.argv)


        if len(arguments) > 3:
            print("Sorry multiple arguments not supported!")

        self.loadTemplates()
        action = arguments[1]

        if (action == "new"):
            self.new_contest()
        elif (action == "archive"):
            self.save_current_contest()
        elif (action == "run"):
            file = arguments[2]
            self.run(file)

        self.loadTemplates()

    #validate current config    
    def checkConfig(self):

        filePath = os.path.join(sys.path[0], "config.json")

        try:

            self.configData = self.readJson(filePath)
            if self.configData is None:
                raise FileNotFoundError

            for items in self.configNames:
                if (len(self.configData[items]) == 0):
                    return False

            return True
                    
        except FileNotFoundError:
            print("no config file found")
            print("creating new file")

            self.configData = {}
            for items in self.configNames:
                self.configData[items] = ""

            self.saveJson(filePath, self.configData)
            return False
            
    def saveJson(self, filePath, data):
        with open(filePath, 'w') as json_file:
            json.dump(data, json_file)

    def readJson(self, filePath):

        data = None
        try:
            with open(filePath, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            return data

    #utility function to run comfiguration process
    def runConfig(self):
        print(self.configData)

        paths = []

        paths.append(os.path.join(sys.path[0], "java_template.py"))
        paths.append(os.path.join(sys.path[0], "python_template.py"))
        paths.append(os.path.join(sys.path[0], "Archives"))
        paths.append(os.path.join(sys.path[0], "code"))

        for i,items in enumerate(self.configNames):
            if len(self.configData[items]) == 0:
                self.configData[items] = paths[i]

                if i == 0:                    
                    with open(paths[0], "w+") as file:
                        file.write("")
                elif i == 1:
                    with open(paths[1], "w+") as file:
                        file.write("")
                elif i == 2:
                    os.mkdir(paths[2])
                elif i == 3:
                    os.mkdir(paths[3])

        print("All files and folders have been created. Add your template code as required!")

        filePath = os.path.join(sys.path[0], "config.json")

        self.saveJson(filePath, self.configData)

    #utility function to update current config
    def updateConfig(self):

        filePath = os.path.join(sys.path[0], "config.json")

        i = 0
        print("Choose the number corresponding to the config that you want to change")
        for items in self.configNames:
            print(items+"............."+i)
            i+=1

        while(True):
            try:
                n = int(input())
                if (n < i and n > 0):
                    print(self.messages[n])
                    inp = input()
                    self.configData[self.configNames[n]] = inp
                    self.saveJson(filePath, self.configData)
            except:
                print("Please enter proper input in the form of an integer")

    # utility func to load the templates
    def loadTemplates(self):
        self.javaTemplate = ""
        with open(self.configData["javaTemplate"], 'r') as javaFile:
            for lines in javaFile:
                self.javaTemplate+=lines

        self.pythonTemplate = ""
        with open(self.configData["pythonTemplate"], 'r') as pythonFile:
            for lines in pythonFile:
                self.pythonTemplate+=lines
            
    '''
        Execute a file
    '''
    def run(self, fileName):

        extension = fileName.split(".")[1]
        prefixFolder = fileName.split("\\")[0]

        fileName = self.configData["workingFolderPath"]+"\\"+fileName
        pathToMain = self.configData["workingFolderPath"]+"\\"+prefixFolder
        outputFilePath = self.configData["workingFolderPath"]+"\\"+prefixFolder+"\\out.out"
        actualOutputFilePath = self.configData["workingFolderPath"]+"\\"+prefixFolder+"\\outActual.out"

        pathToHome = sys.path[0]

        inputFile = open(self.configData["workingFolderPath"]+"\\"+prefixFolder+"\\in.out", "r")
        outputFile = open(outputFilePath, "w+")

        executionTime = 0

        if (extension == "java"):
            p = subprocess.Popen(["javac", fileName])
            while(p.poll() is None):
                pass
            
            os.chdir(pathToMain)
            
            timeStart = datetime.now()
            p = subprocess.Popen(["java", "Main"], stdin=inputFile, stdout=outputFile)
            while(p.poll() is None):
                pass
            executionTime = datetime.now() - timeStart

            os.chdir(pathToHome)

        elif (extension == "py"):

            timeStart = datetime.now()
            p = subprocess.Popen(["python", fileName], stdin=inputFile, stdout=outputFile)

            while(p.poll() is None):
                pass

            executionTime = datetime.now() - timeStart
        
        
        print("Program executed successfully in %ss... running test" %str(executionTime.total_seconds()))
        self.checkOutput(outputFilePath, actualOutputFilePath)

    '''
        Function to check if the two outputs are equal
    '''
    def checkOutput(self, outputFilePath, actualOutputFilePath):
        
        your_output = ""
        with open(outputFilePath, "r") as output_file:
            for line in output_file:
                your_output += str(line)

        your_output = your_output.strip()
        print("YOUR OUTPUT: ")
        print(your_output)

        print()

        expected_output = ""
        with open(actualOutputFilePath, "r") as actual_out:
            for lines in actual_out:
                expected_output+=lines

        expected_output = expected_output.strip()
        print("EXPECTED OUTPUT: ")
        print(expected_output)

        print()

        if (expected_output == your_output):
            print("VERDICT: AC")
        else:
            print("VERDICT: WA")

    '''
        Function to create new workspace
    '''
    def new_contest(self):

        if not os.path.exists(self.configData["workingFolderPath"]):
            os.makedirs(self.configData["workingFolderPath"])

        os.chdir(self.configData["workingFolderPath"])
        existing = 0
        for root, dirs, files in os.walk(".", topdown = False):
            for name in files:
                existing+=1    

        if (existing > 0):
            print("There is an existing contest data inn the workspace.")
            print("Press  1 to archive that data and 2 to delete it!")

            ch = int(input())

            if (ch == 1):
                self.save_current_contest()

            for root, dirs, files in os.walk(".", topdown = False):
                for names in files:
                    os.remove(os.path.join(root,names))

        problems = ["A", "B", "C", "D", "E", "F"]

        for items in problems:
            path = self.configData["workingFolderPath"]+"\\"+items

            if not os.path.exists(path):
                os.makedirs(path)

            signatureJ = "/* Created by Arnab Chanda on %s \n\n*/" %datetime.now()
            
            filename = 'Main.java'
            with open(os.path.join(path, filename), 'w+') as temp_file:
                temp_file.write(signatureJ+self.javaTemplate)
            
            signatureP = "# Created by Arnab Chanda on %s \n \n" %datetime.now()
            filename = 'Main.py'
            with open(os.path.join(path, filename), 'w+') as temp_file:
                temp_file.write(signatureP+self.pythonTemplate)

            filenames = ['in.out', 'out.out', 'outActual.out']

            for files in filenames:
                with open(os.path.join(path, files), 'w+') as temp_file:
                    temp_file.write("")

            os.chdir(self.configData["workingFolderPath"])
                
    '''
        Function to archive contest
    '''        
    def save_current_contest(self):
        
        os.chdir(self.configData["workingFolderPath"])
        lengthJav = len(self.javaTemplate)
        lengthPy = len(self.pythonTemplate)

        problems = ["A", "B", "C", "D", "E", "F"]

        files_to_be_moved = []

        for root, dirs, files in os.walk(".", topdown = False):
            for name in files:
                if ("java" in name):
                    content = ""
                    with open(os.path.join(root, name), "r") as file:
                        for lines in file:
                            content+=lines
                    
                    if (len(content) - lengthJav > 65):
                        files_to_be_moved.append(os.path.join(root, name))
                    

                elif ("py" in name):
                    content = ""

                    with open(os.path.join(root, name), "r") as file:
                        for lines in file:
                            content+=lines
                    
                    if (len(content) - lengthPy > 65):
                        files_to_be_moved.append(os.path.join(root, name))
        

        if (len(files_to_be_moved) == 0):
            print("nothing worth saving here!")
        else:

            print("Enter the round name")
            roundName = input()
            roundName = roundName.replace(" ", "")

            if not os.path.exists(self.configData["archivePath"]):
                os.mkdir(self.configData["archivePath"])

            path = os.path.join(self.configData["archivePath"], roundName)

            if not os.path.exists(path):
                os.mkdir(path)

            os.chdir(path)

            for files in files_to_be_moved:
                newPath = os.path.join(path , files.split("\\")[1])
                filename = files.split("\\")[2]

                if not os.path.exists(newPath):
                    os.mkdir(newPath)

                
                source = self.configData["workingFolderPath"]+"\\"+files[1:]
                destination = newPath+"\\"+filename
                shutil.copyfile(source, destination)


        os.chdir(self.configData["workingFolderPath"])
        for root, dirs, files in os.walk(".", topdown = False):
                for names in files:
                    os.remove(os.path.join(root,names))


if __name__ == '__main__':
    bot = Bot()

    
