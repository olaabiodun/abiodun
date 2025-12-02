def solve(s):
    return s.title()

if __name__ == '__main__':
    import os
    
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    s = input()
    result = solve(s)
    fptr.write(result + '\n')
    fptr.close()
