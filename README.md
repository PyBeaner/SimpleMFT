SimpleMFT
=========

simple ntfs MFT grabber and converter

Thanks to dkovar's https://github.com/dkovar/analyzeMFT and 
    jeffbryner's https://github.com/jeffbryner/pyMFTGrabber
      
This repo'aim is to grabber raw MFT data of you local drive and convert it into a simple structure of paths

pyMFTGrabber is used for a live system.So I changed to use it locally.
And analyzeMFT does a lot of works,but sometimes we may only need part of them

Here is an example
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

I'm sorry I did not do any work on code checking, i.e whether it is a valid raw mft to path to the converter.
and scripts runs without any prompt.
If you need these,Please refer to pyMFTGrabber and analyzeMFT above.
