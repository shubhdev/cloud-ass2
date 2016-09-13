"""
Supports creation/deletion of virtual disks. Disks are allocated blocks
from a list of free block ids.
"""
from collections import deque

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
    self.blocks = []
  def disk_blocks(self):
    return self.blocks

class VFS:
  def __init__(self):
    self.disk_1 = [bytearray(100) for i in range(200)]
    self.disk_2 = [bytearray(100) for i in range(300)]
    self.block_metadata = [BlockInfo() for i in range(500)]
    self.disk_metadata = {}
    self.free_blocks = deque([i for i in range(500)])

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
    if size > len(self.free_blocks):
      print('Out of memory!')
      return False
    # Allocate the first 'size' blocks from free blocks list.
    metadata = DiskInfo()
    while size > 0:
      bid = self.free_blocks.popleft()
      block_data = self.block_metadata[bid]
      block_data.unallocated = False
      block_data.disk_id = id
      metadata.blocks.append(bid)
      size -= 1

    self.disk_metadata[id] = metadata
    return True

  def delete_disk(self, id):
    if not id in self.disk_metadata:
      print('No disk with given id found!')
      return False
    metadata = self.disk_metadata[id]
    for bid in metadata.disk_blocks():
      self.free_blocks.append(bid)
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
      return -1
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
  vfs.create_disk('A', 300) # Should be successful now.
  vfs.print_block_allocation()
  vfs.delete_disk('A')
  vfs.print_block_allocation()
  vfs.create_disk('C', 200)
  vfs.print_block_allocation()

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
  # Test writing to id > 200.
  buff = bytearray(b'shraw')
  vfs.write_block('B', 2, buff)
  vfs.read_block('B',2, rbuff1)
  print(rbuff1.decode('utf-8'))
  # Test reading after deletion
  vfs.delete_disk('B')
  print(vfs.read_block('B',2, rbuff1))

if __name__ == '__main__':
  test_disk_api()
  test_block_api()
