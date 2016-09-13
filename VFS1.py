class BlockInfo:
  def __init__(self):
    self.size = 0

class VFS:
  def __init__(self):
    self.disk_1 = [bytearray(100) for i in range(200)]
    self.disk_2 = [bytearray(100) for i in range(300)]
    self.block_metadata = [BlockInfo() for i in range(500)]

  def write_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      print ("Invalid block no")
      return
    if len(block_info) > 100:
      print ("Block data too big")
      return
    metadata = self.block_metadata[block_no-1]
    metadata.size = len(block_info)
    metadata.free = False
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    block[:len(block_info)] = block_info

  def read_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      print ("Invalid block no")
      return
    metadata = self.block_metadata[block_no-1]
    assert not metadata.free
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    res_size = min(len(block_info), metadata.size)
    block_info[:res_size] = block[:res_size]

def test_block_api():
  vfs = VFS()
  buff1 = bytearray(b'shubham')
  buff2 = bytearray(b'sahil')
  buff3 = bytearray(b'prakhar')
  buff4 = bytearray(b'anupam')
  
  # writing buffers to different blocks successfully
  print('Writing buff1= shubham at 1')
  vfs.write_block(1, buff1)
  print('Writing buff2= sahil at 101')
  vfs.write_block(101, buff2)
  print('Writing buff3= prakhar at 201')
  vfs.write_block(201, buff3)
  print('Writing buff4= anupam at 301')
  vfs.write_block(301, buff4)

  rbuff1 = bytearray(10)
  rbuff2 = bytearray(10)
  rbuff3 = bytearray(10)
  rbuff4 = bytearray(10)
  
  print('Reading rbuff1 from 1 ')
  vfs.read_block(1, rbuff1)
  print('rbuff1 = ', rbuff1.decode('utf-8'))  
  print('Reading rbuff2 from 101 ')
  vfs.read_block(101, rbuff2)
  print('buff2 = ', rbuff2.decode('utf-8'))  
  print('Reading rbuff3 from 201 ')
  vfs.read_block(201, rbuff3)
  print('rbuff3 = ', rbuff3.decode('utf-8'))  
  #Rewriting
  buff4 = (b'gggggggg')
  print('Writing buff4= gggggggg at 301')
  vfs.write_block(301, buff4)
  print('Reading rbuff4 from 301 ')
  vfs.read_block(301, rbuff4)
  print('rbuff4 = ', rbuff4.decode('utf-8'))  

  # unsuccessful writing buffers
  print('Writing at block location 601')
  vfs.write_block(601, buff1)
  print('Reading from block location 601')
  vfs.read_block(601, buff1)

  rbufft1 = bytearray(10)
  rbufft2 = bytearray(2) # Test reading into small buffer.
  vfs.read_block(1, rbufft1)
  vfs.read_block(1, rbufft2)
  print("Reading from block 1 into a smaller buffer rbufft2 of size 2")
  print('rbufft1: ',rbuff1.decode('utf-8'), ' rbufft2:',rbufft2.decode('utf-8'))
  # Test data was copied and not referenced.
  print('Before: buff[0]:{1} rbufft1[0]:{0}'.format(rbuff1[0], buff1[0]))
  buff1[0] = 69
  vfs.read_block(1, rbuff1)
  print("Changing buff[0] to 69")
  print('After: buff:[0]:{1} rbufft1[0]:{0}'.format(rbuff1[0], buff1[0]))

  
  rbuff1 = bytearray(10)
  # Test writing to id > 200.
  buff = bytearray(b'abcde')
  print("Writing 'abcde' at 300 and Reading into rbuff1")
  vfs.write_block(300, buff)
  vfs.read_block(300, rbuff1)
  print('rbuff1 = ', rbuff1.decode('utf-8'))


  # input with greater than 100 bytes length
  print("Writing data with size greater than 1 block") 
  over_buff = bytearray(b'00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000');
  vfs.write_block(2, over_buff)


if __name__ == '__main__':
  test_block_api()