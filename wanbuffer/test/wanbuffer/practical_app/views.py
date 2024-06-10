from django.shortcuts import render,redirect
from django.http import HttpResponse
#REST Frameworke API
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, HTTP_403_FORBIDDEN,HTTP_208_ALREADY_REPORTED
from rest_framework.decorators import api_view
from rest_framework import status
import requests
import re
from .models import UserDetails
from django.urls import reverse
# xlsx File
from io import BytesIO
import xlsxwriter
import openpyxl
import pandas as pd

# Create your views here.
regex = "([a-zA-Z0-9]+(?:[._+-][a-zA-Z0-9]+)*)@([a-zA-Z0-9]+(?:[.-][a-zA-Z0-9]+)*[.][a-zA-Z]{2,})"

def index(request):
    url = reverse('userDetailsAPI')
    response = requests.get(f"http://127.0.0.1:8000{url}")
    result = response.json()
    return render(request,'home.html',{'status':result['status'],'msg':result['msg'],'data':result['data']})


def addUser(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name').strip()
        mobile_no = request.POST.get('mobile_no').strip()
        email = request.POST.get('email').strip()
        gender = request.POST['gender']
        
        if full_name and mobile_no.isdigit() and len(mobile_no) == 10 and re.search(regex,email) and gender:
            
            url = reverse('addUserAPI')
            payload = {'fullname': full_name, 'mobile_no': mobile_no, 'email': email, 'gender': gender}
            response = requests.post(f"http://127.0.0.1:8000{url}", data=payload)
            result = response.json()
            
            return render(request,'add.html',{'status':result['status'],'msg':result['msg']})
        return render(request,'add.html',{'status':0,'msg':"Invalid data!"})
    return render(request,'add.html')

def editUser(request,id):
    url = f"/api/user/list/{id}/"
    response = requests.get(f"http://127.0.0.1:8000{url}")
    result = response.json()
    
    if request.method == "POST":
        full_name = request.POST.get('fullname').strip()
        mobile_no = request.POST.get('mobile_no').strip()
        email = request.POST.get('email').strip()
        gender = request.POST['gender']
        
        if full_name and mobile_no.isdigit() and len(mobile_no) == 10 and re.search(regex,email) and gender:
            
            update_url = f"api/user/update/{id}/"
            payload = {'fullname': full_name, 'mobile_no': mobile_no, 'email': email, 'gender': gender}
            update_response = requests.put(f"http://127.0.0.1:8000/{update_url}", data=payload)
            update_result = update_response.json()
            
            return render(request,'edit.html',{'status':update_result['status'],'msg':update_result['msg'],'data':request.POST})
        
        return render(request,'edit.html',{'status':0,'msg':"Invalid data!"})
    return render(request,'edit.html',{'data':result['data'][0]})

def deleteUser(request,id):
    url = f"/api/user/delete/{id}/"
    response = requests.delete(f"http://127.0.0.1:8000{url}")
    result = response.json()
    return redirect('index')

def dataExport(request):
    url = reverse('userDetailsAPI')
    response = requests.get(f"http://127.0.0.1:8000{url}")
    result = response.json()
    
    download_data = result['data']
    filename = 'user data'
    
    if download_data and filename:
        with BytesIO() as b:
            workbook = xlsxwriter.Workbook(b)
            worksheet = workbook.add_worksheet()
            
            col=0
            row=0
            for each in download_data[0].keys():
                worksheet.write(row, col, each)
                col=col+1
                
            row=row+1
            for value in download_data:
                col=0
                for key, val in value.items():
                    worksheet.write(row, col, str(val))
                    col=col+1
                row=row+1
                
            workbook.close()
            response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
            return response


def dataImport(request):
    if request.method == "POST":
        file_name = request.FILES['file_name']
        importData = pd.read_excel(file_name)
        
        if len(importData.columns) == 4 and importData.columns[0] == "fullname" and importData.columns[1] == "mobile_no" and importData.columns[2] == "email" and importData.columns[3] == "gender":
            errorcsvfile = []
            for index,datalist in importData.iterrows():
                
                if not UserDetails.objects.filter(mobile_no=datalist[1]).exists() :
                
                    url = reverse('addUserAPI')
                    payload = {'fullname': datalist[0], 'mobile_no': datalist[1], 'email': datalist[2], 'gender': datalist[3]}
                    response = requests.post(f"http://127.0.0.1:8000{url}", data=payload)
                    result = response.json()
                else:
                    errordata = [f'{index + 2}',f'{datalist[0]}', f'{datalist[1]}', f'{datalist[2]}', f'{datalist[3]}']
                    errorcsvfile.append(errordata)
            
            download_data = errorcsvfile
            filename = "error data"
            
            if download_data and filename:
                with BytesIO() as b:
                    workbook = xlsxwriter.Workbook(b)
                    worksheet = workbook.add_worksheet()
                    
                    col=0
                    row=0
                    file_column = ['row id','fullname','mobile_no','email','gender']
                    for each in file_column:
                        worksheet.write(row, col, each)
                        col=col+1
                        
                    row=row+1
                    for value in download_data:
                        col=0
                        for val in value:
                            worksheet.write(row, col, str(val))
                            col=col+1
                        row=row+1
                        
                    workbook.close()
                    response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
                    return response
        
            return render(request,'import_data.html',{'status':1,'msg':"success!"})
        return render(request,'import_data.html',{'status':0,'msg':"Invalid file!"})
    return render(request,'import_data.html')

@api_view(['POST'])
def addUserAPI(request):
    try:
        if request.method == "POST":
            user_details = request.data
            if user_details['fullname'] and user_details['mobile_no'].isdigit() and len(user_details['mobile_no']) == 10 and re.search(regex,user_details['email']) and user_details['gender']:
                
                if UserDetails.objects.filter(mobile_no=user_details['mobile_no']).exists() :
                    return Response({"status":0,"msg":"Mobile No already exists!"}, status=HTTP_208_ALREADY_REPORTED)
                
                UserDetails.objects.create(fullname=user_details['fullname'], mobile_no=user_details['mobile_no'], email=user_details['email'], gender=user_details['gender'])
                
                return Response({"status":1,"msg":"Success"}, status=HTTP_200_OK)

            return Response({"status":0,"msg":"Invalid Data!"}, status=HTTP_400_BAD_REQUEST)
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)
    except:
        return Response({"status":0,"msg":"Invalid request!"}, status=HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def UpdateUserListAPI(request,id):
    try:
        if request.method == "PUT":
            if id :
                user_details = request.data
                if user_details['fullname'] and user_details['mobile_no'].isdigit() and len(user_details['mobile_no']) == 10 and re.search(regex,user_details['email']) and user_details['gender']:
                    
                    userIdExisxt = UserDetails.objects.filter(id=id)
                    if not userIdExisxt.exists():
                        return Response({"status":0,"msg":"Invalid user data!"}, status=HTTP_403_FORBIDDEN)
                    
                    if userIdExisxt.filter(mobile_no=user_details['mobile_no']).exists():
                        userIdExisxt.update(fullname=user_details['fullname'], email=user_details['email'], gender=user_details['gender'])
                    else:
                        if userIdExisxt[0].mobile_no != user_details['mobile_no'] :
                            if UserDetails.objects.filter(mobile_no=user_details['mobile_no']).exists():
                                return Response({"status":0,"msg":"Mobile No already exists!"}, status=HTTP_208_ALREADY_REPORTED)
                            else:
                                userIdExisxt.update(fullname=user_details['fullname'], mobile_no=user_details['mobile_no'], email=user_details['email'], gender=user_details['gender'])
                    
                    return Response({"status":1,"msg":"Success"}, status=HTTP_200_OK)
                return Response({"status":0,"msg":"Invalid Data!"}, status=HTTP_400_BAD_REQUEST)
            return Response({"status":0,"msg":"Invalid Data!"}, status=HTTP_400_BAD_REQUEST)
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)
    except:
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def userDetailsAPI(request):
    try:
        if request.method == "GET":
            userData = UserDetails.objects.all().values('id','fullname','mobile_no','email','gender').order_by('-created_date')
            return Response({"status":1,"msg":"Success","data":userData}, status=HTTP_200_OK)
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)
    except:
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def userListAPI(request,id):
    try:
        if request.method == "GET":
            if id :
                userIdExisxt = UserDetails.objects.filter(id=id)
                if not userIdExisxt.exists():
                    return Response({"STATUS":1,"MESSAGE":"Invalid user data!"}, status=HTTP_403_FORBIDDEN)
                
                userList = userIdExisxt.values('id','fullname','mobile_no','email','gender')
                
                return Response({"status":1,"msg":"Success","data":userList}, status=HTTP_200_OK)
            return Response({"STATUS":0,"MESSAGE":"Invalid Data!"}, status=HTTP_400_BAD_REQUEST)
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)
    except:
        return Response({"status":0,"msg":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def deleteUserListAPI(request,id):
    try:
        if request.method == "DELETE":
            if id :
                userIdExisxt = UserDetails.objects.filter(id=id)
                if not userIdExisxt.exists():
                    return Response({"STATUS":1,"MESSAGE":"Invalid user data!"}, status=HTTP_403_FORBIDDEN)
                
                userIdExisxt.delete()
                return Response({"STATUS":1,"MESSAGE":"Success"}, status=HTTP_200_OK)
            return Response({"STATUS":0,"MESSAGE":"Invalid Data!"}, status=HTTP_400_BAD_REQUEST)
        return Response({"STATUS":0,"MESSAGE":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)
    except:
        return Response({"STATUS":0,"MESSAGE":"Invalid method!"}, status=HTTP_400_BAD_REQUEST)