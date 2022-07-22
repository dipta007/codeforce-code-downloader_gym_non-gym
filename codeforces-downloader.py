"""
Thanks to manojpandey for his awesome code from that I got the idea
Link: https://github.com/manojpandey/CodeForces-Code-Downloader
""" 

import urllib.request
import json
import time, os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sys import platform as _platform
import getpass
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

MAX_SUBS = 1000000
MAX_CF_CONTEST_ID = 4444

SUBMISSION_URL = 'http://codeforces.com/contest/{ContestId}/submission/{SubmissionId}'
SUBMISSION_URL_GYM = 'http://codeforces.com/gym/{ContestId}/submission/{SubmissionId}'
USER_INFO_URL = 'http://codeforces.com/api/user.status?handle={handle}&from=1&count={count}'

EXT = {'C++': 'cpp', 'C': 'c', 'Java': 'java', 'Python': 'py', 'Delphi': 'dpr', 'FPC': 'pas', 'C#': 'cs'}
EXT_keys = EXT.keys()

replacer = {'&quot;': '\"', '&gt;': '>', '&lt;': '<', '&amp;': '&', "&apos;": "'"}
keys = replacer.keys()

waitTime = 4

gym = {
	
}

regular = {
	
}

print ( "\nIf you are afraid then check the code, You are smart enough to understand it")
GH_TOKEN = getpass.getpass("Enter your GH_TOKEN: ")
os.environ['GH_TOKEN'] = GH_TOKEN

driver = webdriver.Chrome(ChromeDriverManager().install())

def GetContestName():
	site = "http://codeforces.com/api/contest.list?gym=true"
	contestInfo = urllib.request.urlopen(site).read()
	dic = json.loads(contestInfo)
	if dic["status"] != "OK":
		print ("Oops.. Something went wrong....")
		driver.quit()
		exit(0)

	contests = dic['result']
	for contest in contests:
		contestID = contest['id']
		contestName = contest['name']
		gym[contestID] = contestName

	site = "http://codeforces.com/api/contest.list?gym=false"
	contestInfo = urllib.request.urlopen(site).read()
	dic = json.loads(contestInfo)
	if dic["status"] != "OK":
		print( "Oops.. Something went wrong....")
		driver.quit()
		exit(0)

	contests = dic['result']
	for contest in contests:
		contestID = contest['id']
		contestName = contest['name']
		regular[contestID] = contestName

def get_ext(comp_lang):
	if 'C++' in comp_lang:
		return 'cpp'
	for key in EXT_keys:
		if key in comp_lang:
			return EXT[key]
	return ""

def parse(source_code):
	for key in keys:
		source_code = source_code.replace(key, replacer[key])
	return source_code

def CFLogIn(user, passwd):
	login_site = "http://codeforces.com/enter"
	driver.get(login_site)
	username = driver.find_element_by_id("handleOrEmail")
	password = driver.find_element_by_id("password")
	
	username.send_keys(user)
	password.send_keys(passwd)

	driver.find_element_by_class_name("submit").click()
	time.sleep(waitTime)

	elem = driver.find_elements_by_css_selector("#enterForm > table > tbody > tr.subscription-row > td:nth-child(2) > div > span")
	if len(elem) > 0:
		print ("Invalid Handle / Password")
		driver.quit()
		exit(0)
	time.sleep(waitTime)

def FileNameParse(file):
	avoid = ['<', '>', ':','"', '/', '\\', '|', '?', '*']
	ret = ""
	for ch in file:
		if ch not in avoid:
			ret += ch
	return ret

def GetDownloadedFile(handle):
	path = os.path.join( handle , 'downloaded')
	if os.path.exists(path) == False:
		return []
	file = open(str(path), 'r')
	downloaded = file.readlines()
	downloaded = map(lambda s: s.strip(), downloaded)
	print ("Existing: ", downloaded)
	return downloaded

def SetDownloadedFile(handle, st):
	path = os.path.join( handle , 'downloaded')
	file = open(str(path), 'a')
	file.write( st + "\n" )
	file.close()

def main():
	handle = input("\nEnter your handle: ")
	print ("Next step is password. ;) ")
	print ( "If you are afraid then check the code, You are smart enough to understand it")
	passwd = getpass.getpass("Enter your password: ")

	start_time = time.time()

	CFLogIn(handle, passwd)
	GetContestName()
	downloaded = GetDownloadedFile(handle)

	if not os.path.exists(handle):
		os.makedirs(handle)

	user_info = urllib.request.urlopen(USER_INFO_URL.format(handle=handle, count=MAX_SUBS)).read()
	dic = json.loads(user_info)

	if dic['status'] != 'OK':
		print ('Oops.. Something went wrong...')
		exit(0)

	submissions = dic['result']
	alreadyDone = 0
	for submission in submissions:
		alreadyDone+=1
		completed = float( alreadyDone * 100 ) / float( len(submissions) ) 
		print ("Completed: " + str(completed) + "%")

		if submission['verdict'] == 'OK' and submission['contestId'] < MAX_CF_CONTEST_ID:
			con_id, sub_id = submission['contestId'], submission['id'],
			prob_name, prob_id = submission['problem']['name'], submission['problem']['index']
			comp_lang = submission['programmingLanguage']

			prob =  str(con_id) + str(prob_id)
			if prob in downloaded:
				continue
			
			driver.get(SUBMISSION_URL.format(ContestId=con_id, SubmissionId=sub_id))
			submission_info = driver.find_element_by_xpath("//*[@id=\"pageContent\"]/div[3]/pre").text
			result = (parse(submission_info).replace('\r', ''))
			ext = get_ext(comp_lang)

			con_name = regular.get(con_id, "Unknown Contest")
			
			new_directory = os.path.join( handle, FileNameParse(con_name + " - " + str(con_id)) )
			path = os.path.join( new_directory, FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext )
			# new_directory = handle + '/' + FileNameParse(con_name + " - " + str(con_id))
			# path = new_directory + '/' + FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext;

			if(len(new_directory) > 100):
				new_directory = os.path.join( handle, FileNameParse(str(con_id)))
				path = os.path.join( new_directory, FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext)
				# new_directory = handle + '/' + FileNameParse(str(con_id))
				# path = new_directory + '/' + FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext 

			if not os.path.exists(new_directory):
				os.makedirs(new_directory)

			
			file = open(path, 'wb')

			file.write(result.encode('UTF-8'))
			file.close()
			downloaded.append(str(con_id) + str(prob_id))
			
			print( "                                  Regular - ", str(prob_name.encode('UTF-8')))
			SetDownloadedFile(handle, str(con_id) + str(prob_id))
			time.sleep(waitTime)

		elif submission['verdict'] == 'OK':
			con_id, sub_id = submission['contestId'], submission['id'],
			prob_name, prob_id = submission['problem']['name'], submission['problem']['index']
			comp_lang = submission['programmingLanguage']

			prob = str(con_id) + str(prob_id)
			if prob in downloaded:
				continue

			driver.get(SUBMISSION_URL_GYM.format(ContestId=con_id, SubmissionId=sub_id))

			print(SUBMISSION_URL_GYM.format(ContestId=con_id, SubmissionId=sub_id))

			submission_info = driver.find_element_by_xpath("//*[@id=\"pageContent\"]/div[3]/pre").text
			result = parse(submission_info).replace('\r', '')
			ext = get_ext(comp_lang)
			con_name = gym.get(con_id, "Unknown Contest")
			
			new_directory = os.path.join( handle, FileNameParse(con_name + " - " + str(con_id)) )
			path = os.path.join( new_directory, FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext )
			# new_directory = handle + '/' + FileNameParse(con_name + " - " + str(con_id))
			# path = new_directory + '/' + FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name)  + '.' + ext

			if(len(new_directory) > 100):
				new_directory = os.path.join( handle, FileNameParse(str(con_id)))
				path = os.path.join( new_directory, FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext)
				# new_directory = handle + '/' + FileNameParse(str(con_id))
				# path = new_directory + '/' + FileNameParse(str(con_id) + str(prob_id) + "-" + prob_name) + '.' + ext 

			if not os.path.exists(new_directory):
				os.makedirs(new_directory)

			
			file = open(path, 'wb')

			file.write(bytes(result))
			file.close()
			downloaded.append(str(con_id) + str(prob_id))
			 
			print ("                                  GYM - ", str(prob_name.encode('UTF-8')))
			SetDownloadedFile(handle, str(con_id) + str(prob_id))
			time.sleep(waitTime)

	end_time = time.time()
	driver.quit()

	print ("\n\nSuccessfully Completed 100%")
	print ('Execution time %d seconds' % int(end_time - start_time) )

if __name__ == "__main__":
	main()
