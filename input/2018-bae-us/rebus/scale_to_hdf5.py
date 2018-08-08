import numpy as np
import matplotlib.pyplot as plt
import h5py


class scale_to_hdf5:
    """

        volume: volume in liters (we need kg)
        fertile_rate: units of [g / (seconds MTIHM)]
    """
    def __init__(self, waste_file, core_file, volume,
                 output_db, fertile_rate, fertile_comp, fissile_file='',
                 blanket_file=''):
        self.waste_file = waste_file
        self.core_file = core_file
        self.volume = volume
        self.output_db = output_db
        self.fissile_file = fissile_file
        self.fertile_rate = fertile_rate
        self.fertile_comp = fertile_comp
        self.blanket_file = blanket_file

        self.f = h5py.File(self.output_db, 'w')
        self.get_isos()
        self.get_timestep()
        self.init_hm()
        self.fertile_rate_calc()
        dt = h5py.special_dtype(vlen=str)
        self.f.create_dataset('iso names', data=[x.encode('utf8') for x in self.iso_names],
                              dtype=dt)

        print('\n ==========================')
        print('Initial Heavy Metal: %f kg' %self.init_hm)
        print('Number of Isotopes: %i ' %self.array_size[1])
        print('Total timesteps: %i ' %self.array_size[0])
        print('dt: %i days' %self.dt)
        print('==========================\n')

    def init_hm(self):
        self.read_file(self.core_file)
        hm = 0
        for key, val in self.iso_dict.items():
            el = ''.join([c for c in key if c.isalpha()])
            if el in ['Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm',
                      'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Amm']:
                hm += val[0]
        self.init_hm = hm

    def fertile_rate_calc(self):
        self.rate = self.fertile_rate * self.init_hm * self.dt * 24 * 3600
        fertile_in_dict = {}
        for key, val in self.fertile_comp.items():
            fertile_in_dict[key] = np.zeros(self.timestep) - (self.rate * val)
        self.iso_dict = fertile_in_dict
        self.dict_to_2d()
        self.f.create_dataset('driver refill tank composition', data=self.array)

    def get_timestep(self):
        with open(self.waste_file, 'r') as f:
            lines = f.readlines()
            line = lines[5]
            line = line.split()
            self.dt = float(line[2]) - float(line[1])
            self.f.create_dataset('siminfo_timestep', data=self.dt, dtype=float)

    def read_file(self, file):
        iso_dict = {}
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines[6:-2 ]:
                line = line.split()
                iso = line[0].capitalize()
                iso_dict[iso] = [float(x) * self.volume for x in line[1:]]
        self.iso_dict = iso_dict

    def get_isos(self):
        iso_names = []
        length_list = []
        file_list = [self.waste_file, self.core_file, self.blanket_file,
                     self.fissile_file]
        file_list = [x for x in file_list if x != '']
        for file in file_list:
            self.read_file(file)
            for iso in self.iso_dict.keys():
                iso_names.append(iso)
                length_list.append(len(self.iso_dict[iso]))

        self.iso_names = list(set(iso_names))
        timesteps = list(set(length_list))
        print(len(timesteps))
        if len(timesteps) != 1:
            raise ValueErrror('The timesteps for the files do not match! \n')
        self.timestep = timesteps[0]
        self.array_size = (self.timestep, len(self.iso_dict.keys()))


    def dict_to_2d(self):
        array = np.zeros(self.array_size)
        for iso, val in self.iso_dict.items():
            indx = self.iso_names.index(iso)
            array[:, indx] = val
        self.array = array

    def file_to_db(self, filename, dataset_name, zeros=False):
        if zeros:
            self.f.create_dataset(dataset_name, data=np.zeros(self.array_size))
            return
        self.read_file(filename)
        self.dict_to_2d()
        self.f.create_dataset(dataset_name, data=self.array)

    def main(self):

        self.file_to_db(self.waste_file, 'waste tank composition')
        self.file_to_db(self.core_file, 'driver composition after reproc')
        
        if self.fissile_file == '':
            print('NO FISSILE FILE - Just going to be zeros')
            self.file_to_db(self.fissile_file, 'fissile tank composition', True)
        else:
            self.file_to_db(self.fissile_file, 'fissile tank composition')

        if self.blanket_file == '':
            print('NO Blanket File - Just going to be zeros')
            self.file_to_db(self.blanket_file, 'blanket composition after reproc', True)
        else:
            self.file_to_db(self.blanket_file, 'blanket composition after reproc')

        self.f.close()



# volume in liters
z = scale_to_hdf5(waste_file='./rebus_waste',
                  core_file='./rebus_core',
                  blanket_file='',
                  volume=56200,
                  fertile_rate=3.6325e-4,
                  fertile_comp = {'U235': 0.003,
                                  'U238': 0.997},
                  output_db='output.hdf5',)
z.main()