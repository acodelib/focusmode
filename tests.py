import unittest
from focusmode import FocusMode
import io
import os
from datetime import datetime 
from numpy.distutils.lib2def import FUNC_RE

class TestFocusMode(unittest.TestCase):
#------------------------------------------------------------------------------------------------------------    
#------------------------------------------------- Tests ----------------------------------------------------
#------------------------------------------------------------------------------------------------------------

    def test_isWorkingHours_Focus(self):        
        target_timestamp = datetime.strptime("2021-08-11 14:12:53","%Y-%m-%d %H:%M:%S")
        service = FocusMode()   
        check_result = service.isWorkingHours(target_timestamp)
        
        self.assertTrue(check_result)
        
    def test_isWorkingHours_Free_Weekeng(self):        
        target_timestamp = datetime.strptime("2021-08-14 09:12:53","%Y-%m-%d %H:%M:%S")
        service = FocusMode()   
        check_result = service.isWorkingHours(target_timestamp)
        
        self.assertFalse(check_result)  
    
    def test_isWorkingHours_Free_Morning(self):        
        target_timestamp = datetime.strptime("2021-08-12 08:55:53","%Y-%m-%d %H:%M:%S")   
        service = FocusMode()
        check_result = service.isWorkingHours(target_timestamp)
        
        self.assertFalse(check_result)  
        
    def test_isWorkingHours_Free_Evening(self):        
        target_timestamp = datetime.strptime("2021-08-12 19:00:00","%Y-%m-%d %H:%M:%S")
        service = FocusMode()   
        check_result = service.isWorkingHours(target_timestamp)
        
        self.assertFalse(check_result)  
#------------------------------------------------------------------------------------------------------          
    def test_computeFocusMode_Normal_Free(self):
        target_timestamp = datetime.strptime("2021-08-12 19:00:00","%Y-%m-%d %H:%M:%S")
        env_var = "Normal"
        service = FocusMode()
        check_result = service.computeFocusMode(env_var, target_timestamp)
        
        self.assertEqual("Free", check_result)
        
    def test_computeFocusMode_Normal_Focus(self):
        target_timestamp = datetime.strptime("2021-08-12 10:00:00","%Y-%m-%d %H:%M:%S")
        env_var = "Normal"
        service = FocusMode()
        check_result = service.computeFocusMode(env_var, target_timestamp)
        
        self.assertEqual("Focus", check_result)    
        
    def test_computeFocusMode_Focus(self):
        target_timestamp = datetime.strptime("2021-08-14 10:00:00","%Y-%m-%d %H:%M:%S")
        env_var = "Focus"
        service = FocusMode()
        check_result = service.computeFocusMode(env_var, target_timestamp)
        
        self.assertEqual("Focus", check_result)    
        
    def test_computeFocusMode_Free(self):
        target_timestamp = datetime.strptime("2021-08-12 11:00:00","%Y-%m-%d %H:%M:%S")
        env_var = "Free"
        service = FocusMode()
        check_result = service.computeFocusMode(env_var, target_timestamp)
        
        self.assertEqual("Free", check_result)
#------------------------------------------------------------------------------------------------------
    def test_processEnvironVar_MissingEnvVar(self):
        environ_dummy = {"TESTING":"NOTHING", "THETESTY":"SOMETHING", "OTHER":"OTHERS"}
        service = FocusMode()        
        check_result = service.processEnvironVar(environ_dummy)
        
        self.assertEqual("Normal", check_result)

    def test_processEnvironVar_WrongValue(self):
        environ_dummy = {"TESTING":"NOTHING", "THETESTY":"SOMETHING", "OTHER":"OTHERS", "FOCUSMODECONTROL":"Wrong"}
        service = FocusMode()        
        check_result = service.processEnvironVar(environ_dummy)
        
        self.assertEqual("Normal", check_result)
        
    def test_processEnvironVar_Free(self):
        environ_dummy = {"TESTING":"NOTHING", "THETESTY":"SOMETHING", "OTHER":"OTHERS", "FOCUSMODECONTROL":"Free"}
        service = FocusMode()        
        check_result = service.processEnvironVar(environ_dummy)
        
        self.assertEqual("Free", check_result)
#------------------------------------------------------------------------------------------------------        
    def test_getUrlFromString(self):
        test_str ="some stuff going won www.testingaddr.info this was a url"
        service = FocusMode()
        check_result = service.getUrlFromString(test_str)
        
        self.assertEqual("www.testingaddr.info", check_result)
#------------------------------------------------------------------------------------------------------        
    def test_checkMissingRedirectsFromFile(self):
        url_list = ["www.samba.xx", "www.digi24.info", "www.music.ppp", "www.test.dbf"]
        expected_result = ["www.samba.xx","www.test.dbf"]
        file_text = """

172.11.33.132 www.samba.xx

87.248.114.11 www.music.ppp
87.248.114.11 www.digi24.info
10.101.122.104 www.piupiu.ro
"""
        test_stream = io.StringIO(file_text)
        service = FocusMode()        
        func_result = service.checkMissingRedirectsFromFile(test_stream,url_list)      

        self.assertTrue(set(expected_result) == set(func_result))       
#------------------------------------------------------------------------------------------------------   
    def test_appendRedirects(self):
        url_list = ["www.timesnewroman.ro", "www.wikipedia.ro", "www.facebook.ro"]
        file_text = """
#some random comment
172.11.33.191 www.bla.info

11.08.113.11 www.pic.com
"""
        expected_result ="""
#some random comment
172.11.33.191 www.bla.info

11.08.113.11 www.pic.com
87.248.114.11 www.timesnewroman.ro
87.248.114.11 www.wikipedia.ro
87.248.114.11 www.facebook.ro
"""
        test_stream = io.StringIO(file_text)
        service = FocusMode()        
        service.appendRedirects(test_stream, url_list)                

        self.assertEqual(expected_result, test_stream.getvalue())
                
if __name__ == '__main__':
    unittest.main()    