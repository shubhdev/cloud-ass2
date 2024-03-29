"""
Supports replication of blocks.
Supports creation/deletion of virtual disks. Disks are allocated blocks
from a list of free block ids.
"""
from collections import deque
import random

generate_read_errors = True
read_error_prob = 0.1
class BlockInfo:
  def __init__(self):
    self.size = 0
    self.free = True
    self.unallocated = True
    self.disk_id = None
    self.error = False
    self.replication = None
  
  def reset(self):
    error = self.error
    self.__init__()
    self.error = error

class DiskInfo:
  def __init__(self):
    self.blocks = []
    self.size = 0
  def disk_blocks(self):
    return self.blocks

class VFS:
  def __init__(self):
    self.disk_1 = [bytearray(100) for i in range(200)]
    self.disk_2 = [bytearray(100) for i in range(300)]
    self.block_metadata = [BlockInfo() for i in range(500)]
    self.disk_metadata = {}
    self.free_blocks = deque([i for i in range(500)])
    self.original_read_error = 0;
    self.replica_read_error = 0;
    self.read_error = False;


  def _write_block(self, block_no, block_info):
    if block_no > 500 or block_no < 1:
      print("Invalid block no")
      return False
    if len(block_info) > 100:
      print("Block data too big")
      return False
    metadata = self.block_metadata[block_no-1]
    if metadata.error:
      print ("Corrupted block write at block ", block_no )
      return -1
    metadata.size = len(block_info)
    metadata.free = False
    if block_no <= 200:
      block = self.disk_1[block_no-1]
    else:
      block = self.disk_2[block_no-201]
    block[:len(block_info)] = block_info
    return True

  def _read_block(self, block_no, block_info):
    # Uncomment for testing test_replica()
    # if block_no == 1:
    #   return -1
    if block_no > 500 or block_no < 1:
      print("Invalid block no")
      return -1
    metadata = self.block_metadata[block_no-1]
    if metadata.error:
      print("Corrupted block read from block ", block_no)
      return -1
    if generate_read_errors and random.random() < read_error_prob:
      print ("Random read error")
      self.read_error = True;
      return -1
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
    size = 2*size
    if size > len(self.free_blocks):
      print('Out of memory!')
      return False
    # Allocate the first 'size' blocks from free blocks list.
    metadata = DiskInfo()
    metadata.size = size//2
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

  def find_free_block(self, disk_id):
    blocks = self.disk_metadata[disk_id].disk_blocks()
    size = len(blocks)
    for i in range(size//2,size):
      pid = blocks[i]
      data = self.block_metadata[pid]
      if data.free and not data.error:
        return pid
    return -1
    
  def write_block(self, id, block_no, block_info):
    if not id in self.disk_metadata:
      print('Invalid disk id')
      return False
    metadata = self.disk_metadata[id]
    if block_no > metadata.size or block_no < 1:
      print('Invalid block no')
      return False
    pid = metadata.disk_blocks()[block_no-1]
    if not self._write_block(pid+1, block_info):
      return False
    block_data = self.block_metadata[pid]
    if block_data.replication is None:
      # assign a block for replication.
      rpid = self.find_free_block(id)
      if rpid < 0:
        print ("Not enough space for replication!")
        return True
      block_data.replication = rpid
    if not self._write_block(block_data.replication+1, block_info):
      print('Failed to create replica')
    return True

  def read_block(self, id, block_no, block_info):  
    if not id in self.disk_metadata:
      print('Invalid disk id')
      return -1
    metadata = self.disk_metadata[id]
    if block_no > metadata.size or block_no < 1:
      print('Invalid block no')
      return False

    pid = metadata.disk_blocks()[block_no-1]
    # print('~~~~', pid)
    res = self._read_block(pid+1, block_info)
    if res < 0:
      if(self.read_error):
        self. original_read_error += 1
        self.read_error = False;
      # try for the replication block
      bdata = self.block_metadata[pid]
      bdata.error = True
      rpid = bdata.replication
      if rpid is None:
        print("Error retrieving block")
        return -1
      res = self._read_block(rpid+1, block_info)
      if res < 0:
        if(self.read_error):
          self.replica_read_error += 1
          self.read_error = False;
        print("Error retrieving block")
        self.block_metadata[rpid].error = True
        return -1
      print('Block read from replica')
      # Make original block point towards the replica.
      metadata.disk_blocks()[block_no-1] = rpid
      new_rpid = self.find_free_block(id)
      if new_rpid < 0:
        print("Error creating replica")
        return res
      if self._write_block(new_rpid+1, block_info):
        self.block_metadata[rpid].replication = new_rpid
      return res
    return res

def test_replication():
  vfs = VFS()
  vfs.create_disk('A', 100)
  rbuff = bytearray(20)
  # print(vfs._read_block(201,rbuff)) # Acc. to our design, this should have the replica.
  # print(rbuff.decode('utf-8'))  
  # # If we generate error when bid is 1, should read from replica.
  # # Note update the code for success in this test.
  # print(vfs.read_block('A',1,rbuff))
  # print(rbuff.decode('utf-8'))  

  for i in range(50,101):
    s = "block inforamtion in block number " + str(i);
    b = bytearray()
    b.extend(s.encode())
    vfs.write_block('A',i,b)

  vfs.write_block('A',1, bytearray(b'shubham'))

  for i in range(50,101):
    b = bytearray(50)
    vfs.read_block('A',i,b)
    print("b : " , b.decode('utf-8'))
  print ("# original_read_error : " , vfs.original_read_error)
  print ("# replica read error : " ,vfs.replica_read_error)

  print ("----------------------------------------")

  for i in range(50,101):
    s = "updated block inforamtion in block number " + str(i);
    b = bytearray()
    b.extend(s.encode())
    vfs.write_block('A',i,b)

  for i in range(50,101):
    b = bytearray(50)
    vfs.read_block('A',i,b)
    print("b : " , b.decode('utf-8'))
  
  print ("# original_read_error : " , vfs.original_read_error)
  print ("# replica read error : " ,vfs.replica_read_error)



if __name__ == '__main__':
  test_replication()
