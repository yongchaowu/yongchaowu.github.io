---
layout: post
title: "Code-OPC DA- OPC Client Code Demo"
date: 2020-07-11 15:40:00
categories: ["Code"]
tags: ["OPC", "Code"]
---

{% raw %}
摘自 [A very simple OPC Client: the code](https://lhcb-online.web.cern.ch/ecs/opcevaluation/opcclienttutorial/SimpleClient.html)
https://lhcb-online.web.cern.ch/ecs/opcevaluation/opcclienttutorial/SimpleClient.html

<!--more-->
------
```language
A very simple OPC Client: the code

We want to write a code to instantiante an interface of the OPC server and then release it.
There will be 3 steps:
initialisation of the Microsft® COM® library.
Instantiantion of the IOPCServer interface.
Release of the IOPCServer interface.
closing of the Microsft® COM® library.
Here is the corresponding main function:
void main(void)
{
 // have to be done before using microsoft COM library:
 CoInitialize(NULL);
 // Let's instantiante the IOPCServer interface and get a pointer of it:
 IOPCServer* pServer = InstantiateServer(L"OPC.Evaluation:HV supply.1");

 // release IOPServer interface:
 pServer->Release();

//close the COM library
CoUnitialize();
}

InstantiateServer function
IOPCServer* Instantiate(wchar_t szServerName);
This function instantiate the IOPCServer inteface of the OPCSever whose name is given by the parameter szServerName. It returns a pointer to this interface.
We need first to get the CLSID of the OPCServer. For this purpose we will use the CLSIDFromString function from the Ole32.dll library (header file, objbase.h):

hr = CLSIDFromString(szServerName, &CLSID_OPCServer);
we will get the CLSID in the variable CLSID_OPCServer. hr will be equal to S_OK (=0) if the operation succeded, to an error code if not (see CLSIDFromString).
Now we've got the ingredients to instantiate the IOPCServer interface. We will use the fucntion CoCreateInstanceEx of the ole32.dll library (header file, objbase.h) to do that:

 hr = CoCreateInstanceEx(CLSID_OPCServer, NULL, CLSCTX_SERVER,
  NULL, InterfaceQueueCount, InterfaceQueue);
We want to instantiante only one interface: InterfaceQueueCount has to be at 1. InterfaceQueue is an array of MULTI_IQ's:
typedef struct _MULTI_QI {
        const IID*    pIID;       // the IID of the interface. IID is an GUID that identifie the interface.
        IUnknown *    pItf;        // place to return the Interface pointer.
        HRESULT       hr;
    } MULTI_QI;
For our case we can define and initialize InterfaceQueue as the following:
 MULTI_QI queue[1] =
      {{&IID_OPCServer,
      NULL,
      0}};
IID_OPCServer is defined in OPC_i.c which is created at the compilation of the OPC.idl file.
Here is the code of the InstantiateServer function:
 

IOPCServer* InstantiateServer(wchar_t ServerName[])
{
 CLSID CLSID_OPCServer;
 HRESULT hr;
 // get the CLSID from the OPC Server Name:
 hr = CLSIDFromString(ServerName, &CLSID_OPCServer);
 _ASSERT(!FAILED(hr));
 

 //queue of the class instances to create
 LONG cmq = 1; // nbr of class instance to create.
 MULTI_QI queue[1] =
  {{&IID_OPCServer,
  NULL,
  0}};

 // create an instance of the IOPCServer
 hr = CoCreateInstanceEx(CLSID_OPCServer, NULL, CLSCTX_SERVER,
  &CoServerInfo/*NULL*/, cmq, queue);
 _ASSERT(!hr);

 // return a pointer to the IOPCServer interface:
 return(IOPCServer*) queue[0].pItf;
}

Remark:
This function works if the OPCServer is locally registered. The OPCServer can be remote but it has to be register in the window registry in so far as it Specially you should have the key HKEY_CLASSES_ROOT/AppID/OPCServer_CLSID should have a string "RemoteServerName" containing the network path to the computer containing the OPCServer.
If the OPCServer is not locally registered see Remote Instantiate function.

The complete code:
Click here for SimpleOPCClient_v1.cpp | Click here for SimpleOPCClient_v1.h
 
Remark:
Before running the OPC client you have to install the Proxy.
A simple OPC client that's doing something
Now we have built an OPC client that works but doing no work we will add to it a reading function to read the value of an OPC Item.
This function may look like:
void ReadItem(IUnknown* pGroupIUnknown, OPCHANDLE hServerItem, VARIANT& varValue);
But before reading an item we should fisrt had an OPCGroup, then had the item to this OPCGroup.So we will have two other functions:
void AddTheGroup(IOPCServer* pIOPCServer, IOPCItemMgt* &pIOPCItemMgt, OPCHANDLE& hServerGroup);
void AddTheItem(IOPCItemMgt* pIOPCItemMgt, OPCHANDLE& hServerItem);
and after the reading we need to remove the OPCItem and the OPCGroup:
void RemoveItem(IOPCItemMgt* pIOPCItemMgt, OPCHANDLE hServerItem);
void RemoveGroup (IOPCServer* pIOPCServer, OPCHANDLE hServerGroup);
So the main function will look like:
void main(void)
{
 IOPCServer* pIOPCServer = NULL;  //pointer to IOPServer interface
 IOPCItemMgt* pIOPCItemMgt = NULL; //pointer to IOPCItemMgt interface
 OPCHANDLE hServerGroup; // server handle to the group
 OPCHANDLE hServerItem;  // server handle to the item
 

 // have to be done before using microsoft COM library:
 CoInitialize(NULL);

 // Let's instantiante the IOPCServer interface and get a pointer of it:
 pIOPCServer = InstantiateServer(OPC_SERVER_NAME);

 // Add the OPC group the OPC server and get an handle to the IOPCItemMgt
 //interface:
 AddTheGroup(pIOPCServer, pIOPCItemMgt, hServerGroup);

 // Add the OPC item
  AddTheItem(pIOPCItemMgt, hServerItem);

 //Read the value of the item from device:
 VARIANT varValue; //to stor the read value
 VariantInit(&varValue);
 ReadItem(pIOPCItemMgt, hServerItem, varValue);

 // print the read value:
 cout << "Read value: " << varValue.XVAL << endl;

 // Remove the OPC item:
 RemoveItem(pIOPCItemMgt, hServerItem);

 // Remove the OPC group:
 RemoveGroup(pIOPCServer, hServerGroup);

 // release the interface references:
 pIOPCItemMgt->Release();
 pIOPCServer->Release();

 //close the COM library:
 CoUninitialize();
}

AddTheGroup function
void AddTheGroup(IOPCServer* pIOPCServer, IOPCItemMgt* &pIOPCItemMgt, OPCHANDLE& hServerGroup);
This function uses the function IOPCServer::AddGroupAddGroup(szName, bActive, dwRequestedUpdateRate, hClientGroup, pTimeBias, pPercentDeadband, dwLCID, phServerGroup, pRevisedUpdateRate, riid, ppUnk). The Group is set as inactive, so the UpdateRate is not used (set arbitrarily to 0).
Here is the code:
void AddTheGroup(IOPCServer* pIOPCServer, IOPCItemMgt* &pIOPCItemMgt,
     OPCHANDLE& hServerGroup)
{
 DWORD dwUpdateRate = 0;
 OPCHANDLE hClientGroup = 0;
 // Add an OPC group and get a pointer to the IUnknown I/F:
    HRESULT hr = pIOPCServer->AddGroup(/*szName*/ L"Group1",
  /*bActive*/ FALSE,
  /*dwRequestedUpdateRate*/ dwUpdateRate,
  /*hClientGroup*/ hClientGroup,
  /*pTimeBias*/ 0,
  /*pPercentDeadband*/ 0,
  /*dwLCID*/0,
  /*phServerGroup*/&hServerGroup,
  &dwUpdateRate,
  /*riid*/ IID_IOPCItemMgt,
  /*ppUnk*/ (IUnknown**) &pIOPCItemMgt);
 _ASSERT(!FAILED(hr));
}
 

AddTheItem function
void AddTheItem(IOPCItemMgt* pIOPCItemMgt, OPCHANDLE& hServerItem)

This function uses the function IOPCItemMgt::AddItems(dwCount, pItemArray, ppAddResults, ppErrors).
Here is the code:

void AddTheItem(IOPCItemMgt* pIOPCItemMgt, OPCHANDLE& hServerItem)
{
 HRESULT hr;
 // Array of items to add:
 OPCITEMDEF ItemArray[1] =
 {{
 /*szAccessPath*/ L"",
 /*szItemID*/ ITEM_ID,
 /*bActive*/ FALSE,
 /*hClient*/ 1,
 /*dwBlobSize*/ 0,
 /*pBlob*/ NULL,
 /*vtRequestedDataType*/ VT,
 /*wReserved*/0
 }};

 //Add Result:
 OPCITEMRESULT* pAddResult=NULL;
 HRESULT* pErrors = NULL;

 // Add an Item to the previous Group:
 hr = pIOPCItemMgt->AddItems(1, ItemArray, &pAddResult, &pErrors);
 _ASSERT(!hr);

 // Server handle for the added item:
 hServerItem = pAddResult[0].hServer;

 // release memory allocated by the server:
 CoTaskMemFree(pAddResult->pBlob);

 CoTaskMemFree(pAddResult);
 pAddResult = NULL;

 CoTaskMemFree(pErrors);
 pErrors = NULL;
}

ReadItem function
void ReadItem(IUnknown* pGroupIUnknown, OPCHANDLE hServerItem, VARIANT& varValue)
This function uses the function IOPCSyncIO::Read(dwSource, dwCount, phServer, ppItemValues, ppErrors). To get a pointer to IOPCSyncIO we use the QueryInterface of the OPC group IUnknown interface. The interface passed trough the pGroupIUnknown parameter to the ReadItem function can be any interface of the OPC group that heritates of the IUnknown interface (that is any interface of the OPC group).
Here is the code:
void ReadItem(IUnknown* pGroupIUnknown, OPCHANDLE hServerItem, VARIANT& varValue)
{
 // value of the item:
 OPCITEMSTATE* pValue = NULL;
 //get a pointer to the IOPCSyncIOInterface:
 IOPCSyncIO* pIOPCSyncIO;
 pGroupIUnknown->QueryInterface(__uuidof(pIOPCSyncIO), (void**) &pIOPCSyncIO);

 // read the item value from cache:
 HRESULT* pErrors = NULL; //to store error code(s)
 HRESULT hr = pIOPCSyncIO->Read(OPC_DS_DEVICE, 1, &hServerItem, &pValue, &pErrors);
 _ASSERT(!hr);
 _ASSERT(pValue!=NULL);

 varValue = pValue[0].vDataValue;

 //Release memeory allocated by the OPC server:
 CoTaskMemFree(pErrors);
 pErrors = NULL;

 CoTaskMemFree(pValue);
 pValue = NULL;

 // release the reference to the IOPCSyncIO interface:
 pIOPCSyncIO->Release();
}

RemoveItem function
void RemoveItem(IOPCItemMgt* pIOPCItemMgt, OPCHANDLE hServerItem)
This function uses the function IOPCItemMgt::RemoveItems(dwCount, phServer, ppErrors).
Here is the code:
void RemoveItem(IOPCItemMgt* pIOPCItemMgt, OPCHANDLE hServerItem)
{
 // server handle of items to remove:
 OPCHANDLE hServerArray[1];
 hServerArray[0] = hServerItem;
 //Remove the item:
 HRESULT* pErrors; // to store error code(s)
 HRESULT hr = pIOPCItemMgt->RemoveItems(1, hServerArray, &pErrors);
 _ASSERT(!hr);

 //release memory allocated by the server:
 CoTaskMemFree(pErrors);
 pErrors = NULL;
}

RemoveGroup function
void RemoveGroup (IOPCServer* pIOPCServer, OPCHANDLE hServerGroup)
This function uses the function IOPCServer:: RemoveGroup(hServerGroup, bForce).
Here is the code:
void RemoveGroup (IOPCServer* pIOPCServer, OPCHANDLE hServerGroup)
{
 // Remove the group:
 HRESULT hr = pIOPCServer->RemoveGroup(hServerGroup, FALSE);
 _ASSERT(!hr);
}
The complete code:
Click here for SimpleOPCClient_v2.cpp | Click here for SimpleOPCClient_v2.h
```
{% endraw %}
