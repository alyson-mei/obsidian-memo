
$\hspace{5mm}$ $\huge{\textrm{1. Basics and history}}$
$\hspace{5mm}$ **RAM** - $\textcolor{pink}{\textrm{Random Access Memory}}$.
Modules: **DIMMs** ($\textcolor{pink}{\textrm{Dual Inline Memory Module}}$). Two independent rows of pins. Installed in memory slots (2..4 usually)
Data: Hard Drive $\rightarrow$ RAM $\rightarrow$ CPU. Not enough RAM $\Rightarrow$ some of the data on the hard drive. Then Hard Drive $\leftrightarrow$ RAM $\rightarrow$ CPU.
Requires constant electrical power.

$\hspace{5mm}$ **DRAM** - $\textcolor{pink}{\textrm{Dynamic RAM}}$. Contains capacitors that store information. Need to be refreshed with electricity. *Asynchronously* with the system clock.
$\hspace{5mm}$ **SDRAM** - $\textcolor{pink}{\textrm{Synchronous DRAM}}$. Used today in RAM DIMMs. *Synchronously* with the system clock.

$\hspace{5mm}$ DIMM: $\textcolor{green}{64}$ bits of data/cycle, SIMM: $\textcolor{orange}{32}$ bits/cycle. DIMM: *8 byte wide* ***bus***
Example: $\textcolor{violet}{\textrm{PC-100 SDRAM 256MB}}$ (SDRAM only 8 byte wide bus). 100 in PC-100 means 100 MHz $\Rightarrow$ 100Mhz * 8 bytes = 800 MB/s. PC-133: 133.(3) * 8 bytes = 1066  MB/s. 

$\hspace{5mm}$ **RIMM** - $\textcolor{pink}{\textrm{Rambus Inline Memory Module}}$.  184 pins, debuted in 1999, was a breakthrough. 800 MHz vs 133 MHz SDRAM but only 2 byte wide bus. 1600 MB/s vs 1066 MB/s.

$\hspace{5mm}$ **DDR** - $\textcolor{pink}{\textrm{Double Data Rate}}$. Sends double the amount of data in each clock signal (rice and fall of the clock signal). Example of labeling: $\textcolor{violet}{\textrm{DDR-333MHz PC-2700 2GB SDRAM}}$. Both the clock speed and the total bandwidth. 333.(3) MHz * 8 bytes = 2700 MB/s. $\textcolor{yellow}{184}$ pins.
$\hspace{5mm}$ **DDR2** allows for higher bus speeds than DDR. Uses less power than DDR. $\textcolor{orange}{240}$ pins compared to 184 in DDR. '2' in label. Example:  $\textcolor{violet}{\textrm{DDR2-800MHz PC2-6400 2GB SDRAM}}$.
$\hspace{5mm}$ **DDR3** twice as fast as DDR2. $\textcolor{orange}{240}$ pins. Uses less power than DDR2.  Example:  $\textcolor{violet}{\textrm{DDR3-1600MHz PC3-12800 2GB SDRAM}}$.
$\hspace{5mm}$ **DDR4** twice as fast as DDR2. $\textcolor{green}{288}$ pins. Uses less power than DDR3. Higher range of speed. Example:  $\textcolor{violet}{\textrm{DDR4-4266MHz PC4-34100 2GB SDRAM}}$.

In my Lenovo X390: $\textcolor{violet}{\textrm{RAM 4ATS1G64HZ-2G6E1 8GB SODIMM DDR4 2667MT/s}}$

$\hspace{5mm}$ **ECC** - $\textcolor{pink}{\textrm{Error Correcting Code}}$. Detects if data was correctly processed by the memory module, makes correction if it needs to. 8 memory chips - Non ECC, 9 memory chips - ECC.

$\hspace{5mm}$ $\huge{\textrm{2. Memory timings}}$
$\hspace{5mm}$ **Clock cycle** - electrical pulse in a CPU. During pulse CPU performs a simple task; some instructions take more cycles. **Overclocking**, **overvolting**. 
In my Lenovo X390 CPU-Z shows:
$\textcolor{pink}{\textrm{CAS Latency}}$  (**CL**) 10 | 17 clocks
$\textcolor{pink}{\textrm{RAS to CAS Delay}}$ (**tRCD**) 10 | 17 clocks
$\textcolor{pink}{\textrm{RAS Precharge}}$ (**tRP**) 10 | 17 clocks
$\textcolor{pink}{\textrm{Cycle Time}}$ (**tRAS**) 28 | 39 clocks
$\textcolor{pink}{\textrm{Row Refresh Cycle Time}}$ (**tRFC**) 234 | 420 clocks

Example: 15-16-16-35
$\bullet$ **CAS Latecncy** - $\textcolor{pink}{\textrm{Column Access Strobe}}$. This is the time it takes for the RAM module to start responding to a request for data measured in clock cycles. $\approx$ lower is better. 
$$ \textrm{CAS Latency} / \textrm{RAM Speed} \times 2000 = \textrm{Latency in nanoseconds} $$
Example: DDR4-1866, CAS Latency 13 $\Rightarrow$ True latency of 13.93ns, DDR4-2400, CAS Latency 17 $\Rightarrow$ True latency of 14.17ns
$\bullet$ **tRCD** -  $\textcolor{pink}{\textrm{Row adress to Column adress Delay}}$. Expresses the small delay between row and column access. 
$\bullet$ tRP - $\textcolor{pink}{\textrm{Row Precharge Time}}$. Latency involved in an opening a new row
$\bullet$ tRAS - $\textcolor{pink}{\textrm{Row Active Time}}$. Minimum number of clock cycles that a row must stay open to ensure the data is read or written properly. 

$\hspace{5mm}$ $\huge{\textrm{3. Diving deeper}}$
$\hspace{5mm}$ DRAM vs SSD: 17 nanoseconds vs 50 microseconds (x3000). But much more data in the SSD (3D array). Example: loading time to load a save file; 3D models, textures, etc. go from SSD to DRAM.