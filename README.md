SimpleMFT
=========

simple ntfs MFT grabber and converter

Thanks to dkovar's https://github.com/dkovar/analyzeMFT and 
    jeffbryner's https://github.com/jeffbryner/pyMFTGrabber
      
This repo'aim is to grabber raw MFT data of you local drive and convert it into a simple structure of paths

pyMFTGrabber is used for a live system.So I changed to use it locally:
    from mft_grabber.py import mft_raw_by_drive
    then:
        mft_of_drive = mft_raw_by_drive(DRIVE_NAME) # i.e. 'C', 'D'
        save this data as 'mft__raw_file'
    now you can use SimpleMFT.py to collect file-system info:
        from SimpleMFT import SimpleMFT
        smft = SimpleMFT(/path/to/raw_mft, drive=DRIVE_NAME)
        records = smft.get_records()
        
    The records list don't contains stat info of files/dirs but only contains:
        path's name,
        path's parent directory
        and some other info you may not need
        
    for more details,please use analyzeMFT
