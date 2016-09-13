"""
Supports creation/deletion of virtual disks. Disks are allocated blocks in a 
contigous manner, so fragmentation can occur.
"""
class BlockInfo:
  def __init__(self):
    self.size = 0
    self.free = True
    self.unallocated = True
    self.disk_id = None
  
  def reset(self):
    self.__init__()

class DiskInfo:
  def __init__(self):
    self.size = 0
    self.start = -1
  def disk_blocks(self):
    if self.start < 0:
      raise 'Uninitalized disk!'
    return range(self.start, self.start + self.size)

class VFS:
  def __init__(self):
    self.disk_1 = [bytearray(100) for i in range(200)]
    self.disk_2 = [bytearray(100) for i in range(300)]
    self.block_metadata = [BlockInfo() for i in range(500)]
    self.disk_metadata = {}

  def _write_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      print("Invalid block no")
      return False
    if len(block_info) > 100:
      print("Block data too big")
      return False
    metadata = self.block_metadata[block_no-1]
    metadata.size = len(block_info)
    metadata.free = False
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    block[:len(block_info)] = block_info
    return True

  def _read_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      print("Invalid block no")
      return -1
    metadata = self.block_metadata[block_no-1]
    if metadata.free:
      return 0
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    res_size = min(len(block_info), metadata.size)
    block_info[:res_size] = block[:res_size]
    return res_size

  def create_disk(self, id, size):
    # Check if disk of given id exists
    if id in self.disk_metadata:
      print('A disk with given id exists')
      return False
    if size > 500:
      print('Out of memory!')
      return False
    # find contigous space of 'size' blocks. O(n^2), could be optimized.
    start = -1
    for bid in range(0, 500-size+1):
      if all(x.unallocated for x in self.block_metadata[bid:bid+size]):
        start = bid
        break
    # print('sdasdasaddasds', start, start+size)
    if start < 0:
      print('Out of memory!')
      return False
    for bid in range(start, start+size):
      block_data = self.block_metadata[bid]
      block_data.unallocated = False
      block_data.disk_id = id
    assert self.block_metadata[0] != self.block_metadata[1]
    metadata = DiskInfo()
    self.disk_metadata[id] = metadata
    metadata.start = start
    metadata.size = size
    return True

  def delete_disk(self, id):
    if not id in self.disk_metadata:
      print('No disk with given id found!')
      return False
    metadata = self.disk_metadata[id]
    for bid in metadata.disk_blocks():
      self.block_metadata[bid].reset()
    self.disk_metadata.pop(id)
    return True

  def print_block_allocation(self):
    for bid in range(0, 500):
      metadata = self.block_metadata[bid]
      if metadata.unallocated:
        print('__', end=' ')
      else:
        print(metadata.disk_id, end=' ')
    print('')

  def write_block(self, id, block_no, block_info):
    if not id in self.disk_metadata:
      print('Invalid disk id')
      return False
    metadata = self.disk_metadata[id]
    if block_no>metadata.size:
      print('Invalid block no')
      return False
    pid = metadata.disk_blocks()[block_no-1]+1
    return self._write_block(pid, block_info)

  def read_block(self, id, block_no, block_info):  
    if not id in self.disk_metadata:
      print('Invalid disk id')
      return -1
    metadata = self.disk_metadata[id]
    if block_no>metadata.size:
      print('Invalid block no')
      return False
    pid = metadata.disk_blocks()[block_no-1]+1
    return self._read_block(pid, block_info)


def test_disk_api():
  vfs = VFS()
  print('Testing Disk API')
  print('Creating Disk A of size 100 blocks')
  vfs.create_disk('A', 100)
  print('Creating Disk B of size 200 blocks')
  vfs.create_disk('B', 200)
  print('Creating Disk C of size 200 blocks')
  vfs.create_disk('C', 200)
  print('Block Allocation:')
  vfs.print_block_allocation()
  print('Deleting Disk A')
  vfs.delete_disk('A')
  print('Block Allocation:')
  vfs.print_block_allocation()
  print('Creating Disk A of size 300 Blocks')
  vfs.create_disk('A', 300) # Since contigous allocation, should throw error
  print('Deleting Disk C')
  vfs.delete_disk('C')
  vfs.print_block_allocation()
  print('Creating Disk A of size 300 Blocks')
  vfs.create_disk('A', 300) # Since contigous allocation, should throw error
  print('Creating Disk A of size 50 Blocks')
  vfs.create_disk('A', 50) # Since contigous allocation, should throw error
  print('Creating Disk B of size 100 Blocks')
  vfs.create_disk('B', 100) # Disk already exists
  vfs.print_block_allocation()
  print('Deleting Disk D')
  vfs.delete_disk('D')

def test_block_api():
  print('Testing Block API')
  vfs = VFS()
  print('Creating Disk A of size 5 blocks')
  vfs.create_disk('A', 5)
  print('Creating Disk B of size 4 blocks')
  vfs.create_disk('B', 4)
  print('Writing buff=shubham at block 1 in Disk A')
  buff = bytearray(b'shubham')
  vfs.write_block('A', 1, buff)
  rbuff1 = bytearray(10)
  rbuff2 = bytearray(2) # Test reading into small buffer.
  print('Reading rbuff1 from block 1 in Disk A ')
  vfs.read_block('A',1, rbuff1)
  print('rbuff1 = ', rbuff1.decode('utf-8'))
  vfs.read_block('A',1, rbuff2)
  print('Reading into a smaller buffer rbuff2 of size 2 from Block 1 in Disk A')
  print('rbuff2 = ', rbuff2.decode('utf-8'))


  buff = bytearray(b'abcde')
  print('Writing buff=abcde at block 2 in Disk B')
  vfs.write_block('B', 2, buff)
  print('Reading rbuff1 from block 2 in Disk B ')

  vfs.read_block('B',2, rbuff1)
  print('rbuff1=',rbuff1.decode('utf-8'))

  #Test writing outside block limit 
  print('Writing buff=abcde at block 10 in Disk B')
  vfs.write_block('B', 10, buff)
  # Test reading after deletion
  print('Deleting Disk B')
  vfs.delete_disk('B')
  print('Reading rbuff1 from block 2 in Disk B')
  vfs.read_block('B',2, rbuff1)

if __name__ == '__main__':
  test_disk_api() 
  # print()
  # test_block_api()