import cast.analysers.jee
import re
import os
from cast.analysers import CustomObject, create_link
import cast.analysers.log

#import cast.analysers.log as printf

class MyExtension(cast.analysers.jee.Extension):
    def __init__(self):
        #self.path = r'C:\Users\rup\workspace\active-mq\tests\pack'
        self.tags_list=['ActiveMQConnectionFactory','connectionFactory','createSession','createQueue']
        self.pattern_case1='(\w+)\s+=\s+session.createQueue\("(\w+)"\)'
        self.pattern_case2='(\w+)\s+=\s+session.createQueue\((\w+)\)'
        self.directory="C:/Users/rup/workspace/active-mq/tests/pack/"
        #self.file_content=''
        self.java_files=[]
        self.final_d={}
        self.queue_name=''
        self.pattern_queue_name=''
        
        
    def start_analysis(self, options):
        cast.analysers.log.debug('hello world')
        self.check_activemq_file()
        #cast.analysers.log.debugf.debug("working!!!!!!!!!!!")
        
    
    def check_activemq_file(self):
        
        
           
          
                
        list_tuple=[]                   #list of tuples containing queue_name,role and filename.
        
        
        for root,directories,files in os.walk(self.directory):
        #for filename in os.listdir(self.directory):   
            for filename in files:
                cast.analysers.log.debug("entered here" + ' ' + str(filename))    
                if filename.endswith(".java"):  
                            
                    req_file=os.path.join(root,filename)
                    self.java_files.append(req_file)
            
        cast.analysers.log.debug(str(self.java_files))            #self.java_files is the list of all the java files present in the given dictionary.
        
        cross_check_tags=[]    #list of matched tags.
        
        for file in self.java_files:
            with open(file,'r') as content:
                file_content=content.read()
                
                #content_list=content.readlines()
                
                #self.class_name(content_list)            
                    
            #cast.analysers.log.debug('hello world!!!!') 
        
            for element in self.tags_list:
                check_tag=element
                regex=re.compile(check_tag)
                if regex.search(file_content):
                    cross_check_tags.append(element)
    
            if set(cross_check_tags)==set(self.tags_list):                   #if both list are equal that means all the required tags are present in the file.
                cast.analysers.log.debug('Yes,It is an Activemq file:')
                queue_name,role,file=self.find_queue_name(file,file_content)
                list_tuple.append([queue_name,role,file])
            
            else:
                cast.analysers.log.debug('It is not an activemq file:',file)
        
        cast.analysers.log.debug(str(list_tuple))
        self.queue_dictionary(list_tuple)
        
        
            
        
    def find_queue_name(self,file,file_content):
                regex_queue_variable=re.compile(self.pattern_case2)
                queue_variable=regex_queue_variable.search(file_content)
                regex_queue_string=re.compile(self.pattern_case1)
                queue_string=regex_queue_string.search(file_content)
                
                if queue_string: # if its a string
                    
                    self.queue_name=queue_string.group(2)
                    
                    cast.analysers.log.debug(self.queue_name)
                    
                
                    
                
            
                else:               #if the queue_name is stored in a variable.
                    
                  
                    pattern_queue_name_value=queue_variable.group(2)+'\s=\s'+'"(\w+)"'
                
                    match_queue=re.search(pattern_queue_name_value,file_content)
                    
                    self.queue_name=match_queue.group(1)
                                       #fetching the queue_name from the search result.
                    
                    
                    cast.analysers.log.debug(str(self.queue_name))
                
                
                
                self.pattern_queue_name_value=queue_variable.group(2)+'\s=\s'+'"(\w+)"'
                
                match_queue=re.search(self.pattern_queue_name_value,file_content)
                if match_queue and re.search('createProducer',file_content):        #to identify the role .
                    
                    #self.final_d[queue_name]['producer'].append(file)
                    return(self.queue_name,'producer',file)
               
                elif match_queue and re.search('createConsumer',file_content):
                    return(self.queue_name,'consumer',file)                              #returning (queue_name,role,file) as tuple.
                    
                   
                else:
                    return ('none','none','none')
        
                
                
    
    def queue_dictionary(self,list_tuple):
        list_queue=[]
        dict_queue={}
        
        for tuple in list_tuple:
            list_queue.append(tuple[0])     #tuple[0] is the queue_name.
        
        set_queue=set(list_queue)
        cast.analysers.log.debug(str(set_queue))         #set to store only unique queue_names.
        
        
        for queue in set_queue:
            dict_queue[queue]={}
            l=[]
            l1=[]
        
            for tuple in list_tuple:
                if queue==tuple[0]:
                    if tuple[1]=='producer':
                        l.append(tuple[2])
                        dict_queue[queue][tuple[1]]=l
                    else:
                        l1.append(tuple[2])
                        dict_queue[queue][tuple[1]]=l1


        cast.analysers.log.debug(str(dict_queue))           #final dictionary of queue,producer_name and consumer_name
        self.class_name(set_queue,list_tuple) #call the class_name function and passing set_queue(that contains unique queue names) and list_tuple.
                
    
    def class_name(self,set_queue,list_tuple):      #function to identify the class_name of the class in which the activemq code is present.
        pattern=r'(\w+)\s+class\s+(\w+)\s+\{'       #pattern to identify class name of the file.
        class_pattern=re.compile(pattern)
        class_dict={}
        
        for file in self.java_files:
            with open(file,'r') as content:
                file_content=content.readlines()
                cast.analysers.log.debug(str(file_content))
        
            for queue in set_queue:
                for i,line in enumerate(file_content):
                    if queue in line:
                        if '=' in line:
                            cast.analysers.log.debug(str(i)+str(line))
                            
                            #cast.analysers.log.debug(str(line))
                
                        
                     
            for r,line in enumerate(reversed(file_content)):        #traversing in the reverse direction to find out the class name.
                    if 'class' in line:
                        cast.analysers.log.debug(str(r)+str(line))
                    class_search=class_pattern.search(line)         #searching the pattern(class_name) in the subsequent file.
                    if  class_search:
                        
                        class_name=class_search.group(2)
                        cast.analysers.log.debug("classname:"+str(class_name))
                        for tuple in list_tuple:
                            if file in tuple:
                                tuple.append(class_name)
                           
        cast.analysers.log.debug(str(list_tuple))           #adding the class_name with the subsequent file.
        for queue in set_queue:     
            class_dict[queue]={}
            producer_class_list=[]
            consumer_class_list=[]
        
            for tuple in list_tuple:
                if queue==tuple[0]:
                    if tuple[1]=='producer':
                        producer_class_list.append(tuple[3])          #if the role is producer,adding the class_name to the producer class list
                        class_dict[queue][tuple[1]]=producer_class_list
                    else:
                        consumer_class_list.append(tuple[3])
                        class_dict[queue][tuple[1]]=consumer_class_list #if the role is consumer,adding the class_name to the consumer class list
                    
    
        
         cast.analysers.log.debug(str(class_dict)) 
        
    
        
        
