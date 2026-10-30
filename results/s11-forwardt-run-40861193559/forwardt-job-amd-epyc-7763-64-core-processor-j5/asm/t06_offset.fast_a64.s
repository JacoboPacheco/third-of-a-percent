0000000000001200 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
    1200:	test   %edx,%edx
    1202:	jle    125e <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x5e>
    1204:	mov    (%rsi),%rax
    1207:	mov    0x8(%rsi),%rsi
    120b:	sub    %rax,%rsi
    120e:	sar    $0x2,%rsi
    1212:	mov    (%rdi),%r8
    1215:	mov    0x8(%rdi),%rdi
    1219:	sub    %r8,%rdi
    121c:	sar    $0x2,%rdi
    1220:	movslq %ecx,%rcx
    1223:	mov    %edx,%edx
    1225:	lea    (%r8,%rcx,4),%r8
    1229:	xor    %r9d,%r9d
    122c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    123b:	nopl   0x0(%rax,%rax,1)
    1240:	cmp    %r9,%rsi
    1243:	je     125f <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x5f>
    1245:	lea    (%rcx,%r9,1),%r10
    1249:	cmp    %r10,%rdi
    124c:	jbe    125f <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x5f>
    124e:	mov    (%rax,%r9,4),%r10d
    1252:	mov    %r10d,(%r8,%r9,4)
    1256:	inc    %r9
    1259:	cmp    %r9,%rdx
    125c:	jne    1240 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x40>
    125e:	ret
    125f:	ud2
    1261:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
