"""
Supports snapshots.
Supports creation/deletion of virtual disks. Disks are allocated blocks
from a list of free block ids.
"""
from collections import deque
import copy

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
    self.snapshots = []
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

  def create_checkpoint(self, disk_id):
    if not disk_id in self.disk_metadata:
      print('Invalid disk id')
      return -1
    disk_data = self.disk_metadata[disk_id]
    snapshot = []
    for bid in disk_data.disk_blocks():
      block_info = bytearray(100)
      self._read_block(bid+1, block_info)
      snapshot.append((copy.deepcopy(self.block_metadata[bid]),
                       block_info))
    disk_data.snapshots.append(snapshot)
    return len(disk_data.snapshots)-1
  def rollback(self, disk_id, snapshot_id):
    if not disk_id in self.disk_metadata:
      print('Invalid disk id')
      return False
    disk_data = self.disk_metadata[disk_id]
    if snapshot_id >= len(disk_data.snapshots) or snapshot_id < 0:
      print('Invalid snapshot id')
      return False
    snapshot = disk_data.snapshots[snapshot_id]
    disk_blocks = disk_data.disk_blocks()
    for i in range(len(disk_blocks)):
      bid = disk_blocks[i]
      (block_data,block_info) = snapshot[i]
      self._write_block(bid + 1, block_info)
      self.block_metadata[bid] = block_data

def test_snapshot():
  vfs = VFS()
  print('Creating Disk A of size 5 Blocks')
  vfs.create_disk('A', 5)
  s0 = vfs.create_checkpoint('A')
  print('Created Checkpoint ',s0)
  print('Editing Disk')
  vfs.write_block('A', 1, bytearray(b'cloud'))
  vfs.write_block('A', 2, bytearray(b'assignment'))
  vfs.write_block('A', 4, bytearray(b'disk'))
  vfs.write_block('A', 5, bytearray(b'snapshot'))
  assert vfs.block_metadata[2].free
  block_info = bytearray(20)

  def print_disk():
    print("Disk State")
    for i in range(1,6):
      print(i, end=" ")
      sz = vfs.read_block('A',i,block_info)
      if sz > 0: 
        print(block_info[:sz].decode('utf-8'))
      else:
        print()
    print('----------------')
  print_disk()
  s1 = vfs.create_checkpoint('A')
  print('Created Snapshot ',s1)
  print('Editing Disk')
  vfs.write_block('A', 1, bytearray(b'disk'))
  vfs.write_block('A', 2, bytearray(b'snapshot'))
  vfs.write_block('A', 3, bytearray(b'assignment'))
  vfs.write_block('A', 4, bytearray(b'cloud'))
  vfs.write_block('A', 5, bytearray(b'new'))
  print_disk()
  s2 = vfs.create_checkpoint('A')
  print('Created Snapshot ',s2)
  print('Rolling Back to ',s1)
  vfs.rollback('A',s1)
  print_disk()
  print('Rolling Back to ',s2)
  vfs.rollback('A',s2)
  # assert vfs.block_metadata[2].free  
  print_disk()
  print('Rolling Back to ',s0)
  vfs.rollback('A',s0)
  print_disk()
  print('Editing Disk')
  vfs.write_block('A', 1, bytearray(b'a'))
  vfs.write_block('A', 3, bytearray(b'c'))
  print_disk()
  print('Rolling Back to ',s1)
  vfs.rollback('A',s1)
  print_disk()

if __name__ == '__main__':
  test_snapshot()