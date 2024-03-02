import numpy as np


class Cask_Calcs:
    """
    This class calculates the number of casks needed for
    storing the used fuel with each configuration.
    """
    def __init__(self, elements,  masses, cask_vol,
                 den_kernel, vol_kernel, mass_kernel,
                 vol_triso, mass_triso, den_triso,
                 vol_prism, mass_prism):
        """
        Parameters
        ----------
        elements: str
            str type of elements being loaded into the cask
            options: 'prism', 'triso', 'kernel'
        masses: dict
            dictionary of years and masses of used fuel
            in kg
        cask_vol: float
            fillable volume of a single cask
            in m^3
        vol_kernel: float
            volume of kernels in a TRISO element
            in m^3
        mass_kernel: float
            mass of kernels in a TRISO element
            in kg
        den_kernel: float
            density of fuel kernels in a TRISO element
            in kernals/m^3
        vol_triso: float
            volume of a TRISO element
            in m^3
        mass_triso: float
            mass of a TRISO element
            in kg
        den_triso: float
            density of TRISO elements in a prism element
            in TRISO/m^3
        vol_prism: float
            volume of a prism element
            in m^3
        mass_prism: float
            mass of a prism element
            in kg
        """
        self.masses = masses
        self.cask_vol = cask_vol  # m^3

        self.vol_kernel = vol_kernel  # m^3
        self.mass_kerne = mass_kernel  # kg
        self.den_kernel = den_kernel  # kernels/triso

        self.vol_triso = vol_triso  # m^3
        self.mass_triso = mass_triso  # kg
        self.den_triso = den_triso  # trisos/prism

        self.vol_prism = vol_prism  # m^3
        self.mass_prism = mass_prism  # kg

        self.elements = elements

    def calculate_num_prisms(self):
        """
        Calculate the number of prisms needed
        for each mass.

        Parameters
        ----------
        masses: dict
            a dictionary where keys are years
            and values are masses
        mass_prism: float
            the mass of each prism

        Returns
        -------
        prisms: list
            list of the number of prisms based on the mass
        """
        prisms = []
        for key in self.masses:
            num_prisms = np.round(self.masses[key] / self.mass_prism)
            prisms.append(num_prisms)
        return prisms

    def calculate_num_trisos(self):
        """
        Calculate the number of prisms needed
        for each mass.

        Parameters
        ----------
        masses: dict
            a dictionary where keys are years
            and values are masses
        den_triso: float
            the number of TRISOs in each prism

        Returns
        -------
        trisos: list
            list of the number of TRISOs based on the prisms
        """
        prisms = self.calculate_num_prisms()

        trisos = []
        for year in range(len(prisms)):
            num_trisos = np.round(prisms[year] * self.den_triso)
            trisos.append(num_trisos)
        return trisos

    def calculate_num_kernels(self):
        """
        Calculate the number of kernels for each mass.

        Parameters
        ----------
        masses: dict
            a dictionary where keys are years
            and values are masses
        den_triso: float
            the number of TRISOs in each prism

        Returns
        -------
        trisos: list
            list of the number of TRISOs based on the prisms
        """
        trisos = self.calculate_num_trisos()

        kernels = []
        for year in range(len(trisos)):
            num_kernels = np.round(trisos[year] * self.den_kernel)
            kernels.append(num_kernels)

        return kernels

    def calculate_casks(self):
        """
        Calculate the number of casks needed and
        the leftover material for each year.

        Returns
        -------
        casks: ndarray
            array of the number of casks
        leftovers: ndarray
            array of leftover masses, incorporated
            into the following year's casks

        Notes
        -----
        * the only mass that isn't included in a cask
          is the last leftover

        """
        if self.elements == 'prism':
            elems = self.calculate_num_prisms()
            vol = self.vol_prism
        elif self.elements == 'triso':
            elems = self.calculate_num_trisos()
            vol = self.vol_triso
        elif self.elements == 'kernel':
            elems = self.calculate_num_kernels()
            vol = self.vol_kernel
        else:
            print('The element you tried is not an option')

        casks = np.zeros(len(elems))
        leftovers = np.zeros(len(elems))

        for year in range(len(elems)):
            if year == 0:
                casks[year], leftovers[year] = divmod(elems[year] * vol /
                                                      self.cask_vol, 1)
            else:
                casks[year], leftovers[year] = divmod((elems[year] * vol /
                                                       self.cask_vol) +
                                                      leftovers[year - 1], 1)
        return casks, leftovers

    def __str__(self):
        return f"Calculates the number of casks based on what is going into
        them."
