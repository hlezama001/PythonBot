from botbuilder.core import TurnContext,ActivityHandler,ConversationState,MessageFactory
from botbuilder.dialogs import DialogSet,WaterfallDialog,WaterfallStepContext
from botbuilder.dialogs.prompts import TextPrompt,NumberPrompt,PromptOptions,ChoicePrompt
from botbuilder.dialogs.choices import Choice
import requests
import pymsteams
from shareplum import Site    
from shareplum import Office365    
from shareplum.site import Version    

sharepointUsername = "hlezama@azdemoclient01.onmicrosoft.com"    
sharepointPassword = "ItQs.2021S@ndb0x!!"    
sharepointSite = "https://azdemoclient01.sharepoint.com/sites/site0"    
website = "https://azdemoclient01.sharepoint.com"    
authcookie = Office365(website, username=sharepointUsername,    
password=sharepointPassword).GetCookies()    
site = Site(sharepointSite, version=Version.v2016, authcookie=authcookie) 

class BotDialog(ActivityHandler):
    def __init__(self,conversation:ConversationState):
        self.con_statea = conversation
        self.state_prop = self.con_statea.create_property("dialog_set")
        self.dialog_set = DialogSet(self.state_prop)
        self.dialog_set.add(TextPrompt("text_prompt"))
        self.dialog_set.add(NumberPrompt("number_prompt"))
        self.dialog_set.add(ChoicePrompt(ChoicePrompt.__name__))
        self.dialog_set.add(WaterfallDialog("main_dialog",[self.GetUserName,self.DisplayChoiceList,self.GetProblem, self.waitAgent, self.Completed]))

    async def GetUserName(self,waterfall_step:WaterfallStepContext):
        return await waterfall_step.prompt("text_prompt",PromptOptions(prompt=MessageFactory.text("Favor introducir nombre completo")))
    
    async def DisplayChoiceList(self,waterfall_step:WaterfallStepContext):
        name = waterfall_step._turn_context.activity.text
        waterfall_step.values["name"] = name
        listofchoice = [Choice("A"),Choice("B"),Choice("C")]
        await waterfall_step._turn_context.send_activity("A) No puedo iniciar sesión")
        await waterfall_step._turn_context.send_activity("B) Tengo problemas con un sistema")
        await waterfall_step._turn_context.send_activity("C) Tengo problemas con mi computadora")
        return await waterfall_step.prompt((ChoicePrompt.__name__),
        PromptOptions(prompt=MessageFactory.text("Seleccione el tipo de problema"),choices=listofchoice))
 
    async def GetProblem(self,waterfall_step:WaterfallStepContext):
        choiceoption = waterfall_step.result.value
        if (choiceoption == "A"):
            waterfall_step.values["choiceoption"] = "No puedo iniciar sesión"
        elif (choiceoption == "B"):
            waterfall_step.values["choiceoption"] = "Tengo problemas con un sistema"
        elif (choiceoption == "C"):
            waterfall_step.values["choiceoption"] = "Tengo problemas con mi computadora"
        
        return await waterfall_step.prompt("text_prompt",PromptOptions(prompt=MessageFactory.text("Describa el problema brevemente")))
    
    async def waitAgent(self,waterfall_step:WaterfallStepContext):
        problemd = waterfall_step._turn_context.activity.text
        waterfall_step.values["problem"] = problemd
        name = waterfall_step.values["name"]
        choiceoption = waterfall_step.values["choiceoption"]
        request = f"Name : {name} , Choice: {choiceoption}, Problem : {problemd}"
        teams_connector = pymsteams.connectorcard('https://azdemoclient01.webhook.office.com/webhookb2/0ce88ac6-b9c8-465a-8d62-1304be0e566f@13773ef3-c394-4997-8354-fc43061fa64a/IncomingWebhook/932330c1334447da8f610f9b7b7a62cc/f634a77c-a64c-427d-889d-7f7f1a73ee25')
        teams_connector.text("Nuevo request: " + request)
        teams_connector.send()
        listofchoice = [Choice("Sí"),Choice("No")]
        return await waterfall_step.prompt((ChoicePrompt.__name__),
        PromptOptions(prompt=MessageFactory.text("Ha sido contactado"),choices=listofchoice))
        
    async def Completed(self,waterfall_step:WaterfallStepContext):
        contacted = waterfall_step.result.value
        name = waterfall_step.values["name"]
        problem = waterfall_step.values["problem"] 
        choiceoption = waterfall_step.values["choiceoption"]
        
        if(contacted== "Sí"):
            waterfall_step.values["contacted"] = True
        else:
            waterfall_step.values["contacted"] = False

        contactbool = waterfall_step.values["contacted"]
        await waterfall_step._turn_context.send_activity("Gracias por utilizar nuestros servicios")
        profileinfo = f"Name : {name} , Choice: {choiceoption}, Problem : {problem}, Contactado: {contactbool}"
        await waterfall_step._turn_context.send_activity(profileinfo)
        set_list = site.List('list')    
        my_data = data=[{'name':name,'tipo':choiceoption, 'detalle':problem}]      
        set_list.UpdateListItems(data=my_data, kind='New') 

        return await waterfall_step.end_dialog()
        
    async def on_turn(self,turn_context:TurnContext):
        dialog_context = await self.dialog_set.create_context(turn_context)

        if(dialog_context.active_dialog is not None):
            await dialog_context.continue_dialog()
        else:
            await dialog_context.begin_dialog("main_dialog")
        
        await self.con_statea.save_changes(turn_context)
