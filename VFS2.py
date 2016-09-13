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
      return 0
    metadata = self.block_metadata[block_no-1]
    if metadata.free:
      return 0
    size = metadata.size

    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    res_size = min(len(block_info), len(block))
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
    pid = metadata.disk_blocks()[block_no-1]+1
    return self._write_block(pid, block_info)

  def read_block(self, id, block_no, block_info):  
    if not id in self.disk_metadata:
      print('Invalid disk id')
      return False
    metadata = self.disk_metadata[id]
    pid = metadata.disk_blocks()[block_no-1]+1
    return self._read_block(pid, block_info)


def test_disk_api():
  vfs = VFS()
  vfs.create_disk('A', 100)
  vfs.create_disk('B', 200)
  vfs.create_disk('C', 200)
  vfs.print_block_allocation()
  vfs.delete_disk('A')
  vfs.delete_disk('C')
  vfs.print_block_allocation()
  vfs.create_disk('A', 300) # Since contigous allocation, should throw error

def test_block_api():
  vfs = VFS()
  vfs.create_disk('A', 5)
  vfs.create_disk('B', 4)
  buff = bytearray(b'shubham')
  vfs.write_block('A', 1, buff)
  rbuff1 = bytearray(10)
  rbuff2 = bytearray(2) # Test reading into small buffer.
  vfs.read_block('A',1, rbuff1)
  vfs.read_block('A',1, rbuff2)
  print(rbuff1.decode('utf-8'), rbuff2.decode('utf-8'))
  # Test data was copied and not referenced.
  print('Before: {1} {0}'.format(rbuff1[0], buff[0]))
  buff[0] = 69
  vfs.read_block('A',1, rbuff1)
  print('After: {1} {0}'.format(rbuff1[0], buff[0]))

  # Test writing to id > 200.
  buff = bytearray(b'shraw')
  vfs.write_block('B', 2, buff)
  vfs.read_block('B',2, rbuff1)
  print(rbuff1.decode('utf-8'))
  # Test reading after deletion
  vfs.delete_disk('B')
  print(vfs.read_block('B',2, rbuff1))

if __name__ == '__main__':
  test_block_api() 